# Global QSS Theme for Socratic Terminal GUI
SOCRATIC_DARK_THEME = """
    QMainWindow {
        background-color: #0d1117;
    }
    QWidget {
        color: #e6edf3;
        font-family: 'Segoe UI', 'Ubuntu', 'DejaVu Sans', 'Noto Sans Arabic', sans-serif;
        font-size: 14px;
    }
    QFrame#crashBanner {
        background-color: #1f1315;
        border: 1px solid #da3633;
        border-radius: 8px;
        padding: 10px;
    }
    QTextEdit#chatArea {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 12px;
        line-height: 1.6;
    }
    QLineEdit#inputField {
        background-color: #161b22;
        border: 1px solid #388bfd;
        border-radius: 6px;
        padding: 10px 14px;
        font-size: 14px;
        color: #ffffff;
    }
    QLineEdit#inputField:focus {
        border: 2px solid #58a6ff;
        background-color: #1c2128;
    }
    QPushButton#sendButton {
        background-color: #238636;
        color: #ffffff;
        font-weight: bold;
        border: none;
        border-radius: 6px;
        padding: 10px 24px;
        font-size: 14px;
    }
    QPushButton#sendButton:hover {
        background-color: #2ea043;
    }
    QPushButton#sendButton:disabled {
        background-color: #21262d;
        color: #8b949e;
    }
    QLabel#headerTitle {
        font-size: 16px;
        font-weight: bold;
        color: #58a6ff;
    }
    QLabel#statusBadge {
        font-size: 12px;
        font-weight: bold;
        padding: 4px 10px;
        border-radius: 4px;
    }
"""
