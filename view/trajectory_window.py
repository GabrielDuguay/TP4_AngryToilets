from __future__ import annotations

from typing import Iterable, List, Tuple

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QWidget


class TrajectoryWindow(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.points: List[QPointF] = []
        self.setWindowTitle("Graphique de trajectoire")
        self.resize(400, 300)

    def set_points(self, world_points: Iterable[tuple[float, float]]) -> None:
        self.points = [QPointF(x, y) for x, y in world_points]
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.GlobalColor.white)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setPen(QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.DashLine))
        margin = 30
        painter.drawRect(margin, margin, self.width() - 2 * margin, self.height() - 2 * margin)

        if len(self.points) < 2:
            return

        scaled = self._scaled_points(margin)
        painter.setPen(QPen(QColor(70, 120, 255), 2))
        painter.drawPolyline(*scaled)
        painter.setPen(QPen(QColor(200, 80, 80), 6))
        painter.drawPoint(scaled[-1])

    def _scaled_points(self, margin: int) -> list[QPointF]:
        max_x = max(point.x() for point in self.points)
        max_y = max(point.y() for point in self.points)
        min_x = min(point.x() for point in self.points)
        min_y = min(point.y() for point in self.points)
        width = max(max_x - min_x, 1)
        height = max(max_y - min_y, 1)

        area_width = self.width() - 2 * margin
        area_height = self.height() - 2 * margin

        scaled: list[QPointF] = []
        for p in self.points:
            norm_x = (p.x() - min_x) / width
            norm_y = (p.y() - min_y) / height
            x = margin + norm_x * area_width
            y = margin + (1 - norm_y) * area_height
            scaled.append(QPointF(x, y))
        return scaled
