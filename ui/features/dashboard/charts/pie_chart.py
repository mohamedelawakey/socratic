import math
try:
    from PyQt6.QtWidgets import QWidget
    from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont
    from PyQt6.QtCore import Qt, QRectF, QPointF
except ImportError:
    QWidget = object


class PieChartWidget(QWidget):
    PALETTE = [
        QColor("#388bfd"),  # Vibrant Blue
        QColor("#f0883e"),  # Warm Orange
        QColor("#bc8cff"),  # Vibrant Purple
        QColor("#3fb950"),  # Fresh Green
        QColor("#ff7b72"),  # Coral Red
        QColor("#56d364"),  # Mint
        QColor("#d29922"),  # Gold
    ]

    def __init__(self, data: dict = None, parent=None):
        super().__init__(parent)
        self.data = data or {}
        self.setMinimumSize(260, 220)
        self.setMouseTracking(True)
        self.hovered_index = -1
        self.slice_angles = []

    def set_data(self, data: dict):
        self.data = data or {}
        self.hovered_index = -1
        self.update()

    def mouseMoveEvent(self, event):
        pos = event.position() if hasattr(event, "position") else event.pos()
        center = self._get_chart_center()
        dx = pos.x() - center.x()
        dy = pos.y() - center.y()
        dist = math.sqrt(dx * dx + dy * dy)

        chart_size = self._get_chart_size()
        outer_radius = chart_size / 2
        inner_radius = outer_radius * 0.55

        new_hover = -1
        if inner_radius <= dist <= outer_radius and self.slice_angles:
            angle_rad = math.atan2(dy, dx)
            angle_deg = math.degrees(angle_rad)
            norm_angle = (angle_deg + 90) % 360

            for idx, (label, start_a, sweep_a, count, percent) in enumerate(self.slice_angles):
                if start_a <= norm_angle < start_a + sweep_a:
                    new_hover = idx
                    break

        if new_hover != self.hovered_index:
            self.hovered_index = new_hover
            if hasattr(Qt, "CursorShape"):
                self.setCursor(Qt.CursorShape.PointingHandCursor if new_hover != -1 else Qt.CursorShape.ArrowCursor)
            self.update()

    def leaveEvent(self, event):
        self.hovered_index = -1
        if hasattr(Qt, "CursorShape"):
            self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()

    def _get_chart_size(self):
        return min(self.width() - 40, self.height() - 40)

    def _get_chart_center(self):
        return QPointF(self.width() / 2, self.height() / 2)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if not self.data:
            painter.setPen(QColor("#8b949e"))
            painter.setFont(QFont("Segoe UI", 12))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No error data recorded yet")
            return

        total = sum(self.data.values())
        if total == 0:
            return

        chart_size = self._get_chart_size()
        center = self._get_chart_center()
        chart_rect = QRectF(center.x() - chart_size / 2, center.y() - chart_size / 2, chart_size, chart_size)

        self.slice_angles = []
        current_deg = 0.0

        for idx, (label, count) in enumerate(self.data.items()):
            sweep_deg = (count / total) * 360.0
            percent = int((count / total) * 100)
            self.slice_angles.append((label, current_deg, sweep_deg, count, percent))

            qt_start = int((90 - current_deg) * 16)
            qt_sweep = -int(sweep_deg * 16)

            base_color = self.PALETTE[idx % len(self.PALETTE)]
            if idx == self.hovered_index:
                painter.setBrush(QBrush(base_color.lighter(130)))
                painter.setPen(QPen(QColor("#ffffff"), 3))
            else:
                painter.setBrush(QBrush(base_color))
                painter.setPen(QPen(QColor("#161b22"), 2))

            painter.drawPie(chart_rect, qt_start, qt_sweep)
            current_deg += sweep_deg

        # Center Donut Hole
        hole_size = chart_size * 0.55
        hole_rect = QRectF(
            chart_rect.center().x() - hole_size / 2,
            chart_rect.center().y() - hole_size / 2,
            hole_size,
            hole_size,
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#161b22")))
        painter.drawEllipse(hole_rect)

        # Center Text: Displays Hovered Info or Total Errors
        if self.hovered_index != -1 and self.hovered_index < len(self.slice_angles):
            label, _, _, count, percent = self.slice_angles[self.hovered_index]
            painter.setPen(QColor("#ffffff"))
            painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            painter.drawText(
                QRectF(hole_rect.x() + 4, hole_rect.y() + hole_size * 0.22, hole_size - 8, hole_size * 0.35),
                Qt.AlignmentFlag.AlignCenter,
                f"{count} ({percent}%)",
            )
            painter.setPen(QColor("#58a6ff"))
            painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            painter.drawText(
                QRectF(hole_rect.x() + 4, hole_rect.y() + hole_size * 0.55, hole_size - 8, hole_size * 0.3),
                Qt.AlignmentFlag.AlignCenter,
                label[:15],
            )
        else:
            painter.setPen(QColor("#ffffff"))
            painter.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            painter.drawText(hole_rect, Qt.AlignmentFlag.AlignCenter, f"{total}\nErrors")
