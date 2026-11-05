try:
    from PyQt6.QtWidgets import QWidget
    from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont
    from PyQt6.QtCore import Qt, QRectF
except ImportError:
    QWidget = object


class ActivityLineChart(QWidget):
    """Interactive daily activity bar chart displaying error trends per day."""

    def __init__(self, data: dict = None, translations: dict = None, parent=None):
        super().__init__(parent)
        self.data = data or {}
        self.translations = translations or {}
        self.setMinimumSize(260, 220)
        self.setMouseTracking(True)
        self.hovered_bar = -1
        self.bars = []
        self.sorted_days = []
        self.counts = []

    def set_data(self, data: dict):
        self.data = data or {}
        self.hovered_bar = -1
        self.update()

    def set_translations(self, translations: dict):
        self.translations = translations or {}
        self.update()

    def mouseMoveEvent(self, event):
        pos = event.position() if hasattr(event, "position") else event.pos()
        new_hover = -1
        for i, bar_rect in enumerate(self.bars):
            if bar_rect.contains(pos.x(), pos.y()) or (
                bar_rect.x() <= pos.x() <= bar_rect.right()
                and 0 <= pos.y() <= self.height()
            ):
                new_hover = i
                break

        if new_hover != self.hovered_bar:
            self.hovered_bar = new_hover
            if hasattr(Qt, "CursorShape"):
                self.setCursor(
                    Qt.CursorShape.PointingHandCursor if new_hover != -1 else Qt.CursorShape.ArrowCursor
                )
            self.update()

    def leaveEvent(self, event):
        self.hovered_bar = -1
        if hasattr(Qt, "CursorShape"):
            self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if not self.data:
            painter.setPen(QColor("#8b949e"))
            painter.setFont(QFont("Segoe UI", 12))
            no_act_msg = self.translations.get("chart_no_activity_data", "No activity recorded yet")
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, no_act_msg)
            return

        self.sorted_days = sorted(self.data.keys())
        self.counts = [self.data[k] for k in self.sorted_days]
        max_val = max(max(self.counts), 1)

        left = 40.0
        right = float(self.width() - 25)
        top = 35.0
        bottom = float(self.height() - 40)
        chart_height = bottom - top

        # Grid lines and Y-axis guide values
        painter.setPen(QPen(QColor("#21262d"), 1, Qt.PenStyle.DashLine))
        painter.setFont(QFont("Segoe UI", 9))
        for i in range(3):
            y = top + i * (chart_height / 2)
            painter.drawLine(int(left), int(y), int(right), int(y))
            val = int(max_val - i * (max_val / 2))
            painter.setPen(QColor("#6e7681"))
            painter.drawText(QRectF(0, y - 8, left - 8, 16), Qt.AlignmentFlag.AlignRight, str(val))
            painter.setPen(QPen(QColor("#21262d"), 1, Qt.PenStyle.DashLine))

        num_bars = len(self.sorted_days)
        slot_width = (right - left) / num_bars
        bar_width = min(max(slot_width * 0.5, 18.0), 45.0)

        self.bars = []
        for i, (day, count) in enumerate(zip(self.sorted_days, self.counts)):
            center_x = left + i * slot_width + slot_width / 2
            bar_h = max((count / max_val) * chart_height, 6.0)
            bar_y = bottom - bar_h
            bar_rect = QRectF(center_x - bar_width / 2, bar_y, bar_width, bar_h)
            self.bars.append(bar_rect)

            is_active = (i == self.hovered_bar)
            fill_color = QColor("#58a6ff") if is_active else QColor("#388bfd")
            painter.setPen(QPen(QColor("#79c0ff") if is_active else QColor("#1f6feb"), 1))
            painter.setBrush(QBrush(fill_color))
            painter.drawRoundedRect(bar_rect, 4.0, 4.0)

            # Count badge over bar
            painter.setPen(QColor("#ffffff") if is_active else QColor("#c9d1d9"))
            painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold if is_active else QFont.Weight.Normal))
            painter.drawText(
                QRectF(center_x - 20, bar_y - 18, 40, 16),
                Qt.AlignmentFlag.AlignCenter,
                str(count),
            )

            # Date label below baseline
            short_date = day[5:] if len(day) >= 10 else day
            painter.setPen(QColor("#58a6ff") if is_active else QColor("#8b949e"))
            painter.setFont(QFont("Segoe UI", 9))
            painter.drawText(
                QRectF(center_x - slot_width / 2, bottom + 8, slot_width, 20),
                Qt.AlignmentFlag.AlignCenter,
                short_date,
            )

        # Header summary if hovered
        if self.hovered_bar != -1 and self.hovered_bar < len(self.sorted_days):
            inter_label = self.translations.get("chart_errors_intercepted", "errors intercepted")
            day_text = f"📅 {self.sorted_days[self.hovered_bar]}: {self.counts[self.hovered_bar]} {inter_label}"
            painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            painter.setPen(QColor("#58a6ff"))
            painter.drawText(
                QRectF(10, 8, self.width() - 20, 20),
                Qt.AlignmentFlag.AlignRight,
                day_text,
            )
