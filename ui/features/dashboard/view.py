import threading
try:
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QApplication,
        QPushButton, QScrollArea, QFrame, QTextEdit, QComboBox
    )
    from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer
except ImportError:
    QWidget = object
    QObject = object
    pyqtSignal = lambda: None

from src.events import EventBus
from ui.features.dashboard.charts import PieChartWidget, ActivityLineChart
from ui.features.dashboard.report_exporter import ReportExporter


class _ReportSignals(QObject):
    chunk_received = pyqtSignal(str)
    report_finished = pyqtSignal()


class DashboardView(QWidget):
    back_requested = pyqtSignal()

    def __init__(self, translations: dict, parent=None):
        super().__init__(parent)
        self.translations = translations
        self.setObjectName("dashboardView")
        self.raw_report_markdown = ""
        self.metrics = {}

        self.signals = _ReportSignals()
        self.signals.chunk_received.connect(self._append_report_chunk)
        self.signals.report_finished.connect(self._on_report_finished)

        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 16, 18, 16)
        main_layout.setSpacing(12)

        header_bar = QHBoxLayout()
        self.back_btn = QPushButton(self.translations.get("back_to_session", "← Back to Session"), self)
        self.back_btn.setObjectName("backButton")
        if hasattr(Qt, "CursorShape"):
            self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.clicked.connect(self.back_requested.emit)
        header_bar.addWidget(self.back_btn)

        title_lbl = QLabel(self.translations.get("dashboard_title", "📊 Dashboard"), self)
        title_lbl.setObjectName("headerTitle")
        header_bar.addWidget(title_lbl)
        header_bar.addStretch()
        main_layout.addLayout(header_bar)

        scroll = QScrollArea(self)
        scroll.setObjectName("dashboardScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content_widget = QWidget()
        content_widget.setObjectName("dashboardContent")
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # 1. Metrics Cards Row
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(10)
        self.card_total = self._create_card(self.translations.get("stat_total_errors", "Total Errors"), "0")
        self.card_rate = self._create_card(self.translations.get("stat_solve_rate", "Solve Rate"), "100%")
        self.card_avg = self._create_card(self.translations.get("stat_avg_time", "Avg Solve Time"), "0s")
        self.card_sessions = self._create_card(self.translations.get("stat_total_sessions", "Launches"), "0")

        cards_layout.addWidget(self.card_total)
        cards_layout.addWidget(self.card_rate)
        cards_layout.addWidget(self.card_avg)
        cards_layout.addWidget(self.card_sessions)
        layout.addLayout(cards_layout)

        # 2. Two-Column Split Charts Section
        charts_row = QHBoxLayout()
        charts_row.setSpacing(12)

        pie_box = QFrame()
        pie_box.setObjectName("chartBox")
        pie_layout = QVBoxLayout(pie_box)
        pie_title = QLabel(self.translations.get("chart_error_distribution", "🍩 Error Distribution"), pie_box)
        pie_title.setObjectName("chartSectionTitle")
        self.pie_chart = PieChartWidget({}, self.translations, pie_box)
        pie_layout.addWidget(pie_title)
        pie_layout.addWidget(self.pie_chart)
        charts_row.addWidget(pie_box, stretch=1)

        line_box = QFrame()
        line_box.setObjectName("chartBox")
        line_layout = QVBoxLayout(line_box)
        line_title = QLabel(self.translations.get("chart_daily_activity", "📈 Daily Activity"), line_box)
        line_title.setObjectName("chartSectionTitle")
        self.line_chart = ActivityLineChart({}, self.translations, line_box)
        line_layout.addWidget(line_title)
        line_layout.addWidget(self.line_chart)
        charts_row.addWidget(line_box, stretch=1)

        layout.addLayout(charts_row)

        # 3. AI Report Section
        report_box = QFrame()
        report_box.setObjectName("chartBox")
        report_layout = QVBoxLayout(report_box)
        report_layout.setSpacing(10)

        report_bar = QHBoxLayout()
        self.btn_generate = QPushButton(self.translations.get("generate_report_btn", "✨ Generate AI Report"), report_box)
        self.btn_generate.setObjectName("generateReportBtn")
        if hasattr(Qt, "CursorShape"):
            self.btn_generate.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_generate.clicked.connect(self._on_generate_report_clicked)
        report_bar.addWidget(self.btn_generate)
        report_bar.addStretch()

        self.btn_copy = QPushButton(self.translations.get("copy_btn", "📋 Copy Report"), report_box)
        self.btn_copy.setObjectName("copyBtn")
        if hasattr(Qt, "CursorShape"):
            self.btn_copy.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy.clicked.connect(self._on_copy_clicked)
        self.btn_copy.setEnabled(False)
        report_bar.addWidget(self.btn_copy)

        self.format_combo = QComboBox(report_box)
        self.format_combo.setObjectName("exportFormatCombo")
        if hasattr(Qt, "CursorShape"):
            self.format_combo.setCursor(Qt.CursorShape.PointingHandCursor)
            if self.format_combo.view():
                self.format_combo.view().setCursor(Qt.CursorShape.PointingHandCursor)
                self.format_combo.view().viewport().setCursor(Qt.CursorShape.PointingHandCursor)
        self.format_combo.addItem(self.translations.get("export_format_md", "Markdown (*.md)"), "md")
        self.format_combo.addItem(self.translations.get("export_format_pdf", "PDF Document (*.pdf)"), "pdf")
        self.format_combo.addItem(self.translations.get("export_format_docx", "Word Document (*.docx)"), "docx")
        report_bar.addWidget(self.format_combo)

        self.btn_export = QPushButton(self.translations.get("export_btn", "📥 Export"), report_box)
        self.btn_export.setObjectName("exportBtn")
        if hasattr(Qt, "CursorShape"):
            self.btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_export.clicked.connect(self._on_export_clicked)
        self.btn_export.setEnabled(False)
        report_bar.addWidget(self.btn_export)
        report_layout.addLayout(report_bar)

        self.report_viewer = QTextEdit(report_box)
        self.report_viewer.setObjectName("reportViewer")
        self.report_viewer.setReadOnly(True)
        self.report_viewer.setMinimumHeight(150)
        report_layout.addWidget(self.report_viewer)

        layout.addWidget(report_box)
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def _create_card(self, title: str, value: str) -> QFrame:
        card = QFrame()
        card.setObjectName("statCard")
        clayout = QVBoxLayout(card)
        clayout.setContentsMargins(12, 10, 12, 10)
        clayout.setSpacing(3)

        lbl_val = QLabel(value, card)
        lbl_val.setObjectName("statValue")
        lbl_title = QLabel(title, card)
        lbl_title.setObjectName("statTitle")

        clayout.addWidget(lbl_val)
        clayout.addWidget(lbl_title)
        card.value_label = lbl_val
        return card

    def refresh_metrics(self):
        self.metrics = EventBus.request_dashboard_metrics()
        self.card_total.value_label.setText(str(self.metrics.get("total_errors", 0)))
        self.card_rate.value_label.setText(f"{self.metrics.get('solve_rate', 100)}%")
        self.card_avg.value_label.setText(f"{self.metrics.get('avg_duration', 0)}s")
        self.card_sessions.value_label.setText(str(self.metrics.get("total_launches", 0)))

        self.pie_chart.set_data(self.metrics.get("error_counts", {}))
        self.line_chart.set_data(self.metrics.get("activity_by_day", {}))

    def _on_generate_report_clicked(self):
        self.btn_generate.setEnabled(False)
        self.btn_copy.setEnabled(False)
        self.btn_export.setEnabled(False)
        self.raw_report_markdown = ""
        self.report_viewer.clear()
        self.report_viewer.setPlaceholderText(self.translations.get("generating_report", "⏳ Analyzing..."))

        def worker():
            from ui.translations import TRANSLATIONS
            lang = "Arabic" if self.translations is TRANSLATIONS.get("arabic") else "English"
            try:
                EventBus.request_analytics_report(
                    self.metrics,
                    lang,
                    lambda chunk: self.signals.chunk_received.emit(chunk),
                )
            finally:
                self.signals.report_finished.emit()

        threading.Thread(target=worker, daemon=True).start()

    def _append_report_chunk(self, text: str):
        self.raw_report_markdown += text
        self.report_viewer.setMarkdown(self.raw_report_markdown)
        self.report_viewer.moveCursor(self.report_viewer.textCursor().MoveOperation.End)

    def _on_report_finished(self):
        self.btn_generate.setEnabled(True)
        self.btn_copy.setEnabled(True)
        self.btn_export.setEnabled(True)

    def _on_copy_clicked(self):
        plain_text = ReportExporter.clean_markdown_to_plain(self.raw_report_markdown)
        if not plain_text:
            return

        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(plain_text)
            orig_text = self.translations.get("copy_btn", "📋 Copy Report")
            self.btn_copy.setText(self.translations.get("copy_success", "✔ Copied!"))
            QTimer.singleShot(2000, lambda: self.btn_copy.setText(orig_text))

    def _on_export_clicked(self):
        ReportExporter.handle_export(
            self,
            self.raw_report_markdown,
            self.format_combo.currentData(),
            self.translations.get("export_btn", "Export"),
        )
