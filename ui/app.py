import html
import sys
import threading

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTextEdit, QLineEdit, QPushButton, QLabel, QFrame
    )
    from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QPropertyAnimation, QPoint
    from PyQt6.QtGui import QTextCursor

    HAS_PYQT = True

    class UIBridge(QObject):
        """Bridge to pass messages from background agent threads to the Qt GUI thread."""
        mentor_message_received = pyqtSignal(str, int)
        user_input_requested = pyqtSignal()
        solution_received = pyqtSignal(str)
        evaluator_verdict_received = pyqtSignal(str)
        live_solution_detected = pyqtSignal()
        live_error_detected = pyqtSignal(str)
        llm_error_occurred = pyqtSignal(str)

    bridge = UIBridge()

except (ImportError, OSError):
    HAS_PYQT = False
    QMainWindow = object
    QApplication = None
    Qt = None

    class MockSignal:
        def emit(self, *args, **kwargs):
            pass

        def connect(self, *args, **kwargs):
            pass

    class DummyBridge:
        mentor_message_received = MockSignal()
        user_input_requested = MockSignal()
        solution_received = MockSignal()
        evaluator_verdict_received = MockSignal()
        live_solution_detected = MockSignal()
        live_error_detected = MockSignal()
        llm_error_occurred = MockSignal()

    bridge = DummyBridge()

from src.utils.read_yaml import ReadYaml
from ui.translations import TRANSLATIONS
from ui.styles import SOCRATIC_DARK_THEME
from ui.templates import ChatTemplates
from ui.settings_drawer import SettingsDrawer


_user_reply_event = threading.Event()
_user_reply_text = ""


def wait_for_gui_user_input() -> str:
    _user_reply_event.clear()
    bridge.user_input_requested.emit()
    _user_reply_event.wait()
    return _user_reply_text


def submit_gui_user_input(text: str):
    global _user_reply_text
    _user_reply_text = text
    _user_reply_event.set()


class SocraticWindow(QMainWindow):
    """Pure, clean, fully-localized Socratic Terminal window."""

    def __init__(self, error_type: str, error_message: str, file_path: str, line_number: int, line_content: str):
        super().__init__()
        
        # Load language setting from .socratic.yaml
        config = ReadYaml.read_yaml()
        lang_setting = config.get("socratic_language", "English").strip().lower()
        self.is_arabic = "arab" in lang_setting
        self.translations = TRANSLATIONS["arabic"] if self.is_arabic else TRANSLATIONS["english"]

        self.setWindowTitle(self.translations["app_title"])
        self.resize(880, 640)

        # Dynamic RTL / LTR layout
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if self.is_arabic else Qt.LayoutDirection.LeftToRight)

        self._center_on_screen()
        self.setStyleSheet(SOCRATIC_DARK_THEME)
        self._build_ui(error_type, error_message, file_path, line_number, line_content)
        self._connect_signals()

    def _center_on_screen(self):
        screen = QApplication.primaryScreen()
        if screen:
            screen_geom = screen.availableGeometry()
            x = (screen_geom.width() - self.width()) // 2
            y = (screen_geom.height() - self.height()) // 2
            self.move(x, y)

    def _build_ui(self, error_type: str, error_message: str, file_path: str, line_number: int, line_content: str):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Root layout holding Left (Chat & Main) and Right (Settings Drawer)
        root_h_layout = QHBoxLayout(central_widget)
        root_h_layout.setContentsMargins(0, 0, 0, 0)
        root_h_layout.setSpacing(0)

        # Left / Main Container
        left_container = QWidget(central_widget)
        main_layout = QVBoxLayout(left_container)
        main_layout.setContentsMargins(18, 16, 18, 16)
        main_layout.setSpacing(12)

        # Header Bar
        top_bar = QHBoxLayout()
        header_label = QLabel(self.translations["header_title"], self)
        header_label.setObjectName("headerTitle")
        
        self.dashboard_btn = QPushButton(self.translations.get("dashboard_btn", "📊 Dashboard"), self)
        self.dashboard_btn.setObjectName("dashboardButton")
        if Qt is not None:
            self.dashboard_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.dashboard_btn.clicked.connect(self._on_dashboard_clicked)

        self.settings_btn = QPushButton(self.translations.get("settings_btn", "⚙️ Settings"), self)
        self.settings_btn.setObjectName("settingsButton")
        if Qt is not None:
            self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.clicked.connect(self._toggle_settings_drawer)

        self.status_badge = QLabel(self.translations["status_active"], self)
        self.status_badge.setObjectName("statusBadge")
        self.status_badge.setStyleSheet("color: #3fb950; background-color: #162a1c;")
        
        top_bar.addWidget(header_label)
        top_bar.addStretch()
        top_bar.addWidget(self.dashboard_btn)
        top_bar.addWidget(self.settings_btn)
        top_bar.addWidget(self.status_badge)
        main_layout.addLayout(top_bar)

        # Crash Summary Box
        crash_frame = QFrame(self)
        crash_frame.setObjectName("crashBanner")
        crash_layout = QVBoxLayout(crash_frame)
        crash_layout.setContentsMargins(12, 10, 12, 10)
        crash_layout.setSpacing(4)

        crash_title = QLabel(f"💥 <b>{error_type}</b>: {error_message}", crash_frame)
        crash_title.setStyleSheet("color: #ff7b72; font-size: 15px;")
        crash_title.setTextFormat(Qt.TextFormat.RichText)

        loc_text = self.translations["crash_location"]
        line_text = self.translations["crashing_line"]
        crash_info = QLabel(
            f"📍 {loc_text}: <i>{file_path}:{line_number}</i> &nbsp;&nbsp;|&nbsp;&nbsp; ⚡ {line_text}: <code style='color: #ffffff; background: #2b1d20; padding: 2px 6px;'>{line_content.strip()}</code>",
            crash_frame
        )
        crash_info.setStyleSheet("color: #8b949e; font-size: 13px;")
        crash_info.setTextFormat(Qt.TextFormat.RichText)

        crash_layout.addWidget(crash_title)
        crash_layout.addWidget(crash_info)
        main_layout.addWidget(crash_frame)

        # Chat Feed Area
        self.chat_area = QTextEdit(self)
        self.chat_area.setObjectName("chatArea")
        self.chat_area.setReadOnly(True)
        main_layout.addWidget(self.chat_area, stretch=1)

        # Bottom Input Area
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)

        self.input_field = QLineEdit(self)
        self.input_field.setObjectName("inputField")
        self.input_field.setPlaceholderText(self.translations["placeholder"])
        self.input_field.returnPressed.connect(self._on_send_clicked)
        self.input_field.setEnabled(False)

        self.send_button = QPushButton(self.translations["send_btn"], self)
        self.send_button.setObjectName("sendButton")
        if Qt is not None:
            self.send_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_button.clicked.connect(self._on_send_clicked)
        self.send_button.setEnabled(False)

        input_layout.addWidget(self.input_field, stretch=1)
        input_layout.addWidget(self.send_button)
        main_layout.addLayout(input_layout)

        root_h_layout.addWidget(left_container, stretch=1)

        # Settings Drawer Panel (320px width, hidden initially)
        self.settings_drawer = SettingsDrawer(self.translations, self)
        self.settings_drawer.setFixedWidth(320)
        self.settings_drawer.hide()
        self.settings_drawer.drawer_closed.connect(self._close_settings_drawer)
        self.settings_drawer.settings_saved.connect(self._on_settings_saved)
        root_h_layout.addWidget(self.settings_drawer)

    def _toggle_settings_drawer(self):
        if self.settings_drawer.isVisible():
            self._close_settings_drawer()
        else:
            self._open_settings_drawer()

    def _on_dashboard_clicked(self):
        # Toast Notification popup in the corner that automatically fades out
        self._show_toast(self.translations.get("dashboard_coming_soon", "🚀 Learning Curve Dashboard is coming soon in the next release!"))

    def _show_toast(self, message: str, duration_ms: int = 4000):
        # Safely hide/remove previous toast if it still exists in C++ Qt memory
        old_toast = getattr(self, "_toast_frame", None)
        if old_toast is not None:
            try:
                old_toast.hide()
                old_toast.deleteLater()
            except RuntimeError:
                pass
            self._toast_frame = None

        self._toast_frame = QFrame(self)
        self._toast_frame.setStyleSheet("""
            QFrame {
                background-color: #1f242c;
                border: 1px solid #388bfd;
                border-radius: 8px;
            }
            QLabel {
                color: #58a6ff;
                font-size: 13px;
                font-weight: 600;
                background-color: transparent;
            }
        """)
        toast_layout = QHBoxLayout(self._toast_frame)
        toast_layout.setContentsMargins(16, 10, 16, 10)
        
        lbl = QLabel(message, self._toast_frame)
        toast_layout.addWidget(lbl)
        
        self._toast_frame.adjustSize()
        # Position in top-right corner of the window
        margin_x = 24
        margin_y = 60
        pos_x = max(10, self.width() - self._toast_frame.width() - margin_x)
        self._toast_frame.move(pos_x, margin_y)
        self._toast_frame.show()
        self._toast_frame.raise_()

        # Auto-hide timer that safely removes reference
        def _cleanup():
            toast = getattr(self, "_toast_frame", None)
            if toast is not None:
                try:
                    toast.hide()
                    toast.deleteLater()
                except RuntimeError:
                    pass
                self._toast_frame = None

        QTimer.singleShot(duration_ms, _cleanup)

    def _open_settings_drawer(self):
        self.settings_drawer.load_settings()
        self.settings_drawer.show()
        # Expand window slightly if needed to make space for drawer
        self.resize(self.width() + 40 if self.width() < 950 else self.width(), self.height())

    def _close_settings_drawer(self):
        self.settings_drawer.hide()

    def _on_settings_saved(self):
        self._llm_warned = False
        resume_html = (
            f"<div style='background-color: #162a1c; border: 1px solid #238636; "
            f"border-radius: 8px; padding: 10px; margin: 8px 0; color: #3fb950; font-size: 13px;'>"
            f"<b>{self.translations['llm_retry_success']}</b></div>"
        )
        self.chat_area.append(resume_html)
        self._scroll_to_bottom()

    def _connect_signals(self):
        bridge.mentor_message_received.connect(self._append_mentor_message)
        bridge.user_input_requested.connect(self._enable_user_input)
        bridge.solution_received.connect(self._append_solution)
        bridge.evaluator_verdict_received.connect(self._append_verdict)
        bridge.live_solution_detected.connect(self._on_live_solution_detected)
        bridge.live_error_detected.connect(self._on_live_error_detected)
        bridge.llm_error_occurred.connect(self._on_llm_error_occurred)

    def _on_llm_error_occurred(self, err_msg: str):
        if hasattr(self, "_llm_warned") and self._llm_warned:
            return
        self._llm_warned = True

        escaped_err = html.escape(err_msg[:120])
        warn_html = (
            f"<div style='background-color: #272115; border: 1px solid #d29922; "
            f"border-radius: 8px; padding: 12px; margin: 8px 0; color: #e3b341; font-size: 13px;'>"
            f"<b>{self.translations['llm_config_needed']}</b><br/>"
            f"<span style='color: #8b949e; font-size: 11px;'>Details: {escaped_err}...</span>"
            f"</div>"
        )
        self.chat_area.append(warn_html)
        self._scroll_to_bottom()

        # Automatically pop open the settings drawer for the user!
        if not self.settings_drawer.isVisible():
            self._open_settings_drawer()

    def _on_live_solution_detected(self):
        self.status_badge.setText(self.translations["status_solved"])
        self.status_badge.setStyleSheet("color: #ffffff; background-color: #238636;")

        celebration_html = (
            f"<div style='background-color: #162a1c; border: 1px solid #238636; "
            f"border-radius: 8px; padding: 12px; margin: 8px 0; color: #3fb950; font-size: 14px;'>"
            f"<b>{self.translations['live_solved_msg']}</b></div>"
        )
        self.chat_area.append(celebration_html)
        self._scroll_to_bottom()

        # Switch send button to Close button
        self.input_field.setEnabled(False)
        self.send_button.setEnabled(True)
        self.send_button.setText(self.translations["close_btn"])
        self.send_button.setStyleSheet("background-color: #238636; color: #ffffff;")
        try:
            self.send_button.clicked.disconnect()
        except TypeError:
            pass
        self.send_button.clicked.connect(self.close)

        # Release background worker thread if waiting for user input
        submit_gui_user_input("q")

    def closeEvent(self, event):
        """Signals session cancellation to background workers when window closes."""
        from src.events import EventBus
        EventBus.emit_session_cancelled()
        submit_gui_user_input("q")
        event.accept()

    def _on_live_error_detected(self, error_trace: str):
        retry_html = (
            f"<div style='background-color: #2b1d20; border: 1px solid #da3633; "
            f"border-radius: 8px; padding: 10px; margin: 8px 0; color: #ff7b72; font-size: 13px;'>"
            f"<b>{self.translations['live_retry_msg']}</b></div>"
        )
        self.chat_area.append(retry_html)
        self._scroll_to_bottom()

    def _append_mentor_message(self, content: str, hint_level: int):
        html_msg = ChatTemplates.mentor_bubble(
            content=content,
            hint_level=hint_level,
            mentor_name=self.translations["mentor_tag"],
            hint_label=self.translations["hint_level"],
            is_arabic=self.is_arabic,
        )
        self.chat_area.append(html_msg)
        self._scroll_to_bottom()

    def _enable_user_input(self):
        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)
        self.input_field.setFocus()

    def _on_send_clicked(self):
        text = self.input_field.text().strip()
        if not text:
            return

        self.input_field.clear()
        self.input_field.setEnabled(False)
        self.send_button.setEnabled(False)

        user_html = ChatTemplates.user_bubble(
            text=text,
            user_tag=self.translations["user_tag"],
            is_arabic=self.is_arabic,
        )
        self.chat_area.append(user_html)
        self._scroll_to_bottom()

        submit_gui_user_input(text)

    def _append_verdict(self, verdict: str):
        badge_html = ChatTemplates.verdict_badge(verdict)
        self.chat_area.append(badge_html)
        self._scroll_to_bottom()

    def _append_solution(self, content: str):
        self.status_badge.setText(self.translations["status_solved"])
        self.status_badge.setStyleSheet("color: #ffffff; background-color: #238636;")

        sol_html = ChatTemplates.solution_bubble(
            content=content,
            wrapup_title=self.translations["wrapup_title"],
        )
        self.chat_area.append(sol_html)
        self._scroll_to_bottom()

        # Switch send button to Close Session button
        self.input_field.setEnabled(False)
        self.send_button.setEnabled(True)
        self.send_button.setText(self.translations["close_btn"])
        self.send_button.setStyleSheet("background-color: #238636; color: #ffffff;")
        try:
            self.send_button.clicked.disconnect()
        except TypeError:
            pass
        self.send_button.clicked.connect(self.close)

    def _scroll_to_bottom(self):
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.chat_area.setTextCursor(cursor)
