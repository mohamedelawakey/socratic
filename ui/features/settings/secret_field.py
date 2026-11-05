try:
    from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton
    from PyQt6.QtCore import Qt
except ImportError:
    QWidget = object
    Qt = None


class SecretInputField(QWidget):
    """Specialized input field masking secret API keys with eye toggle."""

    def __init__(self, raw_value: str = "", placeholder: str = "", tooltip: str = "", parent=None):
        super().__init__(parent)
        self.raw_value = raw_value or ""

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.line_edit = QLineEdit(self)
        self.line_edit.setProperty("class", "settingsInput")
        self.line_edit.setPlaceholderText(placeholder)
        if hasattr(QLineEdit, "EchoMode"):
            self.line_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.line_edit.setText(self.raw_value)
        self.line_edit.textEdited.connect(self._on_user_edit)

        self.eye_btn = QPushButton("👁️", self)
        self.eye_btn.setObjectName("eyeButton")
        self.eye_btn.setToolTip(tooltip or "Show / Hide Secret")
        if Qt is not None and hasattr(Qt, "CursorShape"):
            self.eye_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.eye_btn.clicked.connect(self.toggle_mask)

        layout.addWidget(self.line_edit, stretch=1)
        layout.addWidget(self.eye_btn)

    def _on_user_edit(self, new_text: str):
        self.raw_value = new_text

    def toggle_mask(self):
        if not hasattr(QLineEdit, "EchoMode"):
            return
        if self.line_edit.echoMode() == QLineEdit.EchoMode.Password:
            self.line_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.eye_btn.setText("🔒")
        else:
            self.line_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.eye_btn.setText("👁️")

    def get_value(self) -> str:
        return self.line_edit.text().strip()

    def set_value(self, value: str):
        self.raw_value = value or ""
        self.line_edit.setText(self.raw_value)

