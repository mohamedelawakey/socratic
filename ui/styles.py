SOCRATIC_DARK_THEME = """
    QMainWindow { background-color: #0d1117; }
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
    QPushButton#sendButton:hover { background-color: #2ea043; }
    QPushButton#sendButton:disabled { background-color: #21262d; color: #8b949e; }
    QLabel#headerTitle { font-size: 16px; font-weight: bold; color: #58a6ff; }
    QLabel#statusBadge { font-size: 12px; font-weight: bold; padding: 4px 10px; border-radius: 4px; }
    QPushButton#settingsButton, QPushButton#dashboardButton {
        background-color: transparent;
        color: #8b949e;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 4px 10px;
        font-size: 13px;
        font-weight: 500;
    }
    QPushButton#settingsButton:hover, QPushButton#dashboardButton:hover {
        background-color: #21262d;
        color: #58a6ff;
        border-color: #58a6ff;
    }
    QFrame#settingsDrawer {
        background-color: #161b22;
        border-left: 1px solid #30363d;
    }
    QLabel#drawerTitle { font-size: 16px; font-weight: bold; color: #58a6ff; }
    QLabel#drawerDesc { font-size: 12px; color: #8b949e; }
    QLabel#fieldLabel { font-size: 12px; font-weight: 600; color: #c9d1d9; margin-top: 4px; }
    QLineEdit.settingsInput, QComboBox.settingsCombo {
        background-color: #0d1117;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 6px 10px;
        color: #ffffff;
        font-size: 13px;
    }
    QLineEdit.settingsInput:focus, QComboBox.settingsCombo:focus { border: 1px solid #58a6ff; }
    QPushButton#eyeButton {
        background-color: #0d1117;
        border: 1px solid #30363d;
        border-radius: 6px;
        color: #8b949e;
        padding: 6px 8px;
        font-size: 14px;
    }
    QPushButton#eyeButton:hover { background-color: #21262d; color: #58a6ff; border-color: #58a6ff; }
    QPushButton#closeDrawerBtn {
        background-color: transparent;
        color: #8b949e;
        border: none;
        font-size: 16px;
        font-weight: bold;
        padding: 2px 6px;
        border-radius: 4px;
    }
    QPushButton#closeDrawerBtn:hover { background-color: #21262d; color: #ff7b72; }
    QPushButton#saveSettingsBtn {
        background-color: #238636;
        color: #ffffff;
        font-weight: bold;
        border: none;
        border-radius: 6px;
        padding: 10px;
        font-size: 14px;
        margin-top: 8px;
    }
    QPushButton#saveSettingsBtn:hover { background-color: #2ea043; }
    QPushButton#backButton {
        background-color: #21262d;
        color: #58a6ff;
        border: 1px solid #388bfd;
        border-radius: 6px;
        padding: 6px 14px;
        font-size: 13px;
        font-weight: bold;
    }
    QPushButton#backButton:hover { background-color: #388bfd; color: #ffffff; }
    QWidget#dashboardView {
        background-color: #0d1117;
    }
    QScrollArea#dashboardScroll {
        background: transparent;
        border: none;
    }
    QWidget#dashboardContent {
        background: transparent;
    }
    QFrame#statCard {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 10px 14px;
    }
    QLabel#statValue { font-size: 22px; font-weight: bold; color: #58a6ff; }
    QLabel#statTitle {
        font-size: 11px;
        color: #8b949e;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    QFrame#chartBox {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 14px;
    }
    QLabel#chartSectionTitle {
        font-size: 14px;
        font-weight: bold;
        color: #e6edf3;
        margin-bottom: 4px;
    }
    QTextEdit#reportViewer {
        background-color: #0d1117;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 12px;
        font-size: 13px;
        line-height: 1.6;
        color: #e6edf3;
    }
    QPushButton#generateReportBtn {
        background-color: #238636;
        color: #ffffff;
        font-weight: bold;
        border: 1px solid #2ea043;
        border-radius: 6px;
        padding: 9px 18px;
        font-size: 13px;
    }
    QPushButton#generateReportBtn:hover { background-color: #2ea043; border-color: #3fb950; }
    QPushButton#generateReportBtn:disabled { background-color: #21262d; color: #8b949e; border-color: #30363d; }
    QComboBox#exportFormatCombo {
        background-color: #0d1117;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 6px 12px;
        color: #e6edf3;
        font-size: 12px;
    }
    QComboBox#exportFormatCombo QAbstractItemView {
        background-color: #161b22;
        color: #e6edf3;
        selection-background-color: #388bfd;
        selection-color: #ffffff;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 4px;
        outline: none;
    }
    QPushButton#exportBtn {
        background-color: #1f6feb;
        color: #ffffff;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 13px;
        font-weight: bold;
    }
    QPushButton#exportBtn:hover { background-color: #388bfd; }
    QPushButton#exportBtn:disabled { background-color: #21262d; color: #8b949e; }
    QPushButton#copyBtn {
        background-color: #21262d;
        color: #c9d1d9;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 8px 14px;
        font-size: 12px;
        font-weight: 500;
    }
    QPushButton#copyBtn:hover { background-color: #30363d; color: #ffffff; }
    QPushButton#copyBtn:disabled { background-color: #161b22; color: #8b949e; border-color: #21262d; }
    QToolTip {
        background-color: #1c2128;
        color: #ffffff;
        border: 1px solid #388bfd;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 13px;
        font-family: 'Segoe UI', sans-serif;
    }
"""
