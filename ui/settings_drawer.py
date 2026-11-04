try:
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
        QPushButton, QScrollArea, QFrame, QComboBox
    )
    from PyQt6.QtCore import Qt, pyqtSignal
except ImportError:
    QWidget = object

    class _MockSignal:
        def emit(self, *args, **kwargs):
            pass

        def connect(self, *args, **kwargs):
            pass

    def pyqtSignal():
        return _MockSignal()

from src.utils.config_manager import ConfigManager


class SecretInputField(QWidget):
    """
    A specialized input field for secret keys (like api_key, LANGSMITH_API_KEY).
    Masks the secret by default while showing a preview prefix (e.g. 'sk-1234••••••••'),
    and provides an Eye icon button to toggle full visibility and editing.
    """

    def __init__(self, raw_value: str = "", placeholder: str = "", parent=None):
        super().__init__(parent)
        self.raw_value = raw_value or ""
        self.is_masked = True

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.line_edit = QLineEdit(self)
        self.line_edit.setProperty("class", "settingsInput")
        self.line_edit.setPlaceholderText(placeholder)
        self.line_edit.textEdited.connect(self._on_user_edit)

        self.eye_btn = QPushButton("👁️", self)
        self.eye_btn.setObjectName("eyeButton")
        self.eye_btn.setToolTip("Show / Hide Secret")
        if Qt is not None:
            self.eye_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.eye_btn.clicked.connect(self.toggle_mask)

        layout.addWidget(self.line_edit, stretch=1)
        layout.addWidget(self.eye_btn)

        self._render_text()

    def _render_text(self):
        if not self.raw_value:
            self.line_edit.setText("")
            return

        if self.is_masked:
            prefix_len = min(7, len(self.raw_value))
            prefix = self.raw_value[:prefix_len]
            masked_part = "•" * max(6, len(self.raw_value) - prefix_len)
            self.line_edit.setText(f"{prefix}{masked_part}")
        else:
            self.line_edit.setText(self.raw_value)

    def _on_user_edit(self, new_text: str):
        # When user edits directly, update raw_value
        self.raw_value = new_text

    def toggle_mask(self):
        self.is_masked = not self.is_masked
        if not self.is_masked:
            self.eye_btn.setText("🔒")
            self.line_edit.setText(self.raw_value)
        else:
            self.eye_btn.setText("👁️")
            self._render_text()

    def get_value(self) -> str:
        return self.raw_value

    def set_value(self, value: str):
        self.raw_value = value or ""
        self._render_text()


class SettingsDrawer(QFrame):
    """
    Collapsible side drawer panel for modifying .socratic.yaml settings directly from the GUI.
    """
    settings_saved = pyqtSignal()
    drawer_closed = pyqtSignal()

    def __init__(self, translations: dict, parent=None):
        super().__init__(parent)
        self.translations = translations
        self.setObjectName("settingsDrawer")
        self._build_ui()
        self.load_settings()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(10)

        # Header with Title and Close button
        header_layout = QHBoxLayout()
        title_label = QLabel(self.translations.get("settings_title", "⚙️ Settings"), self)
        title_label.setObjectName("drawerTitle")

        close_btn = QPushButton("✕", self)
        close_btn.setObjectName("closeDrawerBtn")
        if Qt is not None:
            close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.drawer_closed.emit)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        main_layout.addLayout(header_layout)

        desc_label = QLabel(self.translations.get("settings_desc", "Configure LLM provider and API secrets"), self)
        desc_label.setObjectName("drawerDesc")
        desc_label.setWordWrap(True)
        main_layout.addWidget(desc_label)

        # Scroll Area for Form fields
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setContentsMargins(0, 6, 0, 6)
        form_layout.setSpacing(8)

        # 1. Provider
        form_layout.addWidget(self._make_label(self.translations.get("provider_label", "Provider:")))
        self.provider_combo = QComboBox(form_widget)
        self.provider_combo.setProperty("class", "settingsCombo")
        self.provider_combo.addItems(["ollama", "openrouter", "google", "openai"])
        self.provider_combo.setEditable(True)
        form_layout.addWidget(self.provider_combo)

        # 2. Provider Model Name
        form_layout.addWidget(self._make_label(self.translations.get("provider_name_label", "Model Name:")))
        self.provider_name_edit = QLineEdit(form_widget)
        self.provider_name_edit.setProperty("class", "settingsInput")
        form_layout.addWidget(self.provider_name_edit)

        # 3. Provider Link
        form_layout.addWidget(self._make_label(self.translations.get("provider_link_label", "Provider URL:")))
        self.provider_link_edit = QLineEdit(form_widget)
        self.provider_link_edit.setProperty("class", "settingsInput")
        form_layout.addWidget(self.provider_link_edit)

        # 4. API Key (Secret with eye toggle)
        form_layout.addWidget(self._make_label(self.translations.get("api_key_label", "API Key:")))
        self.api_key_field = SecretInputField("", "Enter API key...", form_widget)
        form_layout.addWidget(self.api_key_field)

        # 5. Language
        form_layout.addWidget(self._make_label(self.translations.get("language_label", "Language:")))
        self.language_combo = QComboBox(form_widget)
        self.language_combo.setProperty("class", "settingsCombo")
        self.language_combo.addItems(["Arabic", "English"])
        form_layout.addWidget(self.language_combo)

        # 6. Style
        form_layout.addWidget(self._make_label(self.translations.get("style_label", "Style:")))
        self.style_combo = QComboBox(form_widget)
        self.style_combo.setProperty("class", "settingsCombo")
        self.style_combo.addItems(["friendly", "academic", "concise"])
        form_layout.addWidget(self.style_combo)

        # Separator line
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #30363d; margin: 8px 0;")
        form_layout.addWidget(sep)

        # 7. LangSmith Tracing
        form_layout.addWidget(self._make_label(self.translations.get("langsmith_tracing_label", "LangSmith Tracing:")))
        self.tracing_combo = QComboBox(form_widget)
        self.tracing_combo.setProperty("class", "settingsCombo")
        self.tracing_combo.addItems(["true", "false"])
        form_layout.addWidget(self.tracing_combo)

        # 8. LangSmith API Key (Secret with eye toggle)
        form_layout.addWidget(self._make_label(self.translations.get("langsmith_key_label", "LangSmith API Key:")))
        self.langsmith_key_field = SecretInputField("", "lsv2_pt_...", form_widget)
        form_layout.addWidget(self.langsmith_key_field)

        # 9. LangSmith Project
        form_layout.addWidget(self._make_label(self.translations.get("langsmith_project_label", "LangSmith Project:")))
        self.langsmith_project_edit = QLineEdit(form_widget)
        self.langsmith_project_edit.setProperty("class", "settingsInput")
        form_layout.addWidget(self.langsmith_project_edit)

        form_layout.addStretch()
        scroll.setWidget(form_widget)
        main_layout.addWidget(scroll, stretch=1)

        # Status feedback label
        self.save_feedback_label = QLabel("", self)
        self.save_feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.save_feedback_label.setStyleSheet("color: #3fb950; font-size: 13px; font-weight: bold;")
        self.save_feedback_label.hide()
        main_layout.addWidget(self.save_feedback_label)

        # Save Button
        self.save_btn = QPushButton(self.translations.get("save_settings_btn", "💾 Save Settings"), self)
        self.save_btn.setObjectName("saveSettingsBtn")
        if Qt is not None:
            self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_settings)
        main_layout.addWidget(self.save_btn)

    def _make_label(self, text: str) -> QLabel:
        lbl = QLabel(text, self)
        lbl.setObjectName("fieldLabel")
        return lbl

    def load_settings(self):
        cfg = ConfigManager.load_config()

        # Provider
        prov = str(cfg.get("provider", "ollama"))
        idx = self.provider_combo.findText(prov, Qt.MatchFlag.MatchFixedString)
        if idx >= 0:
            self.provider_combo.setCurrentIndex(idx)
        else:
            self.provider_combo.setEditText(prov)

        self.provider_name_edit.setText(str(cfg.get("provider_name", "")))
        self.provider_link_edit.setText(str(cfg.get("provider_link", "")))
        self.api_key_field.set_value(str(cfg.get("api_key", "")))

        # Language
        lang = str(cfg.get("socratic_language", "English"))
        idx = self.language_combo.findText(lang, Qt.MatchFlag.MatchFixedString)
        if idx >= 0:
            self.language_combo.setCurrentIndex(idx)

        # Style
        style = str(cfg.get("socratic_style", "friendly"))
        idx = self.style_combo.findText(style, Qt.MatchFlag.MatchFixedString)
        if idx >= 0:
            self.style_combo.setCurrentIndex(idx)

        # LangSmith
        tracing = str(cfg.get("LANGSMITH_TRACING", "true")).lower()
        idx = self.tracing_combo.findText(tracing, Qt.MatchFlag.MatchFixedString)
        if idx >= 0:
            self.tracing_combo.setCurrentIndex(idx)

        self.langsmith_key_field.set_value(str(cfg.get("LANGSMITH_API_KEY", "")))
        self.langsmith_project_edit.setText(str(cfg.get("LANGSMITH_PROJECT", "")))

    def save_settings(self):
        new_values = {
            "provider": self.provider_combo.currentText().strip(),
            "provider_name": self.provider_name_edit.text().strip(),
            "provider_link": self.provider_link_edit.text().strip(),
            "api_key": self.api_key_field.get_value().strip(),
            "socratic_language": self.language_combo.currentText().strip(),
            "socratic_style": self.style_combo.currentText().strip(),
            "LANGSMITH_TRACING": self.tracing_combo.currentText().strip(),
            "LANGSMITH_API_KEY": self.langsmith_key_field.get_value().strip(),
            "LANGSMITH_PROJECT": self.langsmith_project_edit.text().strip(),
        }

        success = ConfigManager.save_config(new_values)
        if success:
            self.save_feedback_label.setText(self.translations.get("settings_saved_msg", "✔ Settings saved!"))
            self.save_feedback_label.setStyleSheet("color: #3fb950; font-size: 13px; font-weight: bold;")
            self.save_feedback_label.show()
            self.settings_saved.emit()
        else:
            self.save_feedback_label.setText(self.translations.get("settings_save_error", "❌ Error saving"))
            self.save_feedback_label.setStyleSheet("color: #ff7b72; font-size: 13px; font-weight: bold;")
            self.save_feedback_label.show()

