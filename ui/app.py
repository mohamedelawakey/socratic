import sys
import threading
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QTextCursor

from src.utils.read_yaml import ReadYaml
from ui.translations import TRANSLATIONS
from ui.styles import SOCRATIC_DARK_THEME
from ui.templates import ChatTemplates


class UIBridge(QObject):
    """Bridge to pass messages from background agent threads to the Qt GUI thread."""
    mentor_message_received = pyqtSignal(str, int)
    user_input_requested = pyqtSignal()
    solution_received = pyqtSignal(str)
    evaluator_verdict_received = pyqtSignal(str)


bridge = UIBridge()
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
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(18, 16, 18, 16)
        main_layout.setSpacing(12)

        # Header Bar
        top_bar = QHBoxLayout()
        header_label = QLabel(self.translations["header_title"], self)
        header_label.setObjectName("headerTitle")
        
        self.status_badge = QLabel(self.translations["status_active"], self)
        self.status_badge.setObjectName("statusBadge")
        self.status_badge.setStyleSheet("color: #3fb950; background-color: #162a1c;")
        
        top_bar.addWidget(header_label)
        top_bar.addStretch()
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
        self.send_button.clicked.connect(self._on_send_clicked)
        self.send_button.setEnabled(False)

        input_layout.addWidget(self.input_field, stretch=1)
        input_layout.addWidget(self.send_button)
        main_layout.addLayout(input_layout)

    def _connect_signals(self):
        bridge.mentor_message_received.connect(self._append_mentor_message)
        bridge.user_input_requested.connect(self._enable_user_input)
        bridge.solution_received.connect(self._append_solution)
        bridge.evaluator_verdict_received.connect(self._append_verdict)

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

    def _scroll_to_bottom(self):
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.chat_area.setTextCursor(cursor)
