from __future__ import annotations

from typing import Iterable

import pymunk
from PyQt6.QtCore import QPointF, Qt, QTimer
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen
from PyQt6.QtWidgets import QWidget

from controller.game_controller import GameController
from model.game_model import GameModel


class GameView(QWidget):
    def __init__(self, model: GameModel, controller: GameController, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.model = model
        self.controller = controller
        self.setMinimumSize(model.width, model.height)
        self.setMouseTracking(True)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_frame)
        self.timer.start(16)

    def on_frame(self) -> None:
        self.controller.update_world(1 / 60)
        self.update()

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton:
            self.controller.start_drag(self.height(), event.position())

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.controller.update_drag(self.height(), event.position())

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton:
            self.controller.release_drag(self.height(), event.position())

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.draw_background(painter)
        self.draw_slingshot(painter)
        self.draw_shapes(painter, self.model.get_shapes())
        self.draw_trajectory(painter)

    def draw_background(self, painter: QPainter) -> None:
        painter.fillRect(self.rect(), QColor(230, 240, 255))
        # TODO: Charger une image de fond personnalisée et utiliser painter.drawPixmap

    def draw_slingshot(self, painter: QPainter) -> None:
        origin, stretched = self.controller.get_slingshot_line(self.height())
        painter.setPen(QPen(QColor(80, 50, 30), 6))
        painter.setBrush(QBrush(QColor(120, 70, 40)))
        painter.drawEllipse(origin, 10, 10)

        # TODO: Remplacer les formes du lance-pierre par un visuel personnalisé (PNG/SVG)
        if stretched is not None:
            painter.setPen(QPen(QColor(60, 30, 20), 3))
            painter.drawLine(origin, stretched)

    def draw_shapes(self, painter: QPainter, shapes: Iterable[pymunk.Shape]) -> None:
        for shape in shapes:
            if isinstance(shape, pymunk.Circle):
                self.draw_circle(painter, shape)
            elif isinstance(shape, pymunk.Poly):
                self.draw_polygon(painter, shape)
            elif isinstance(shape, pymunk.Segment):
                self.draw_segment(painter, shape)

    def draw_circle(self, painter: QPainter, circle: pymunk.Circle) -> None:
        center = self._world_to_qt(circle.body.position)
        radius = circle.radius
        painter.setBrush(QBrush(QColor(90, 160, 255)))
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawEllipse(center, radius, radius)
        # TODO: Remplacer la boule par une image personnalisée via painter.drawPixmap

    def draw_polygon(self, painter: QPainter, poly: pymunk.Poly) -> None:
        vertices = [self._world_to_qt(v) for v in GameModel.poly_world_vertices(poly)]
        if not vertices:
            return
        painter.setBrush(QBrush(QColor(200, 140, 100)))
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.drawPolygon(*vertices)

    def draw_segment(self, painter: QPainter, segment: pymunk.Segment) -> None:
        a = self._world_to_qt(segment.a)
        b = self._world_to_qt(segment.b)
        painter.setPen(QPen(QColor(50, 100, 50), segment.radius * 2))
        painter.drawLine(a, b)

    def draw_trajectory(self, painter: QPainter) -> None:
        points = self.controller.get_trajectory(self.height())
        if len(points) < 2:
            return
        painter.setPen(QPen(QColor(255, 80, 80, 180), 2))
        painter.drawPolyline(*points)

    def _world_to_qt(self, position: pymunk.Vec2d) -> QPointF:
        return QPointF(position.x, self.height() - position.y)
