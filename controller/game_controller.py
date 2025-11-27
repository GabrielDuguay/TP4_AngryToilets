from __future__ import annotations

from typing import Optional

import pymunk
from PyQt6.QtCore import QPointF

from model.game_model import GameModel


class GameController:
    def __init__(self, model: GameModel) -> None:
        self.model = model
        self.dragging = False
        self.launched = False

    def _qt_to_world(self, widget_height: int, position: QPointF) -> pymunk.Vec2d:
        return pymunk.Vec2d(position.x(), widget_height - position.y())

    def _world_to_qt(self, widget_height: int, position: pymunk.Vec2d) -> QPointF:
        return QPointF(position.x, widget_height - position.y)

    def start_drag(self, widget_height: int, position: QPointF) -> None:
        if self.model.current_ball is None:
            return
        world_pos = self._qt_to_world(widget_height, position)
        ball_pos = self.model.current_ball.body.position
        if (world_pos - ball_pos).length <= self.model.projectile_radius * 1.4:
            self.dragging = True
            self.launched = False

    def update_drag(self, widget_height: int, position: QPointF) -> None:
        if not self.dragging or self.model.current_ball is None:
            return
        world_pos = self._qt_to_world(widget_height, position)
        clamped = self.model.clamp_drag_position(world_pos)
        self.model.current_ball.body.position = clamped
        self.model.current_ball.body.velocity = (0, 0)

    def release_drag(self, widget_height: int, position: QPointF) -> None:
        if not self.dragging:
            return
        self.dragging = False
        if self.model.current_ball is None:
            return
        world_pos = self._qt_to_world(widget_height, position)
        self.model.launch_projectile(world_pos)
        self.launched = True

    def reset_projectile(self) -> None:
        self.model.reset_projectile()
        self.dragging = False
        self.launched = False

    def update_world(self, dt: float) -> None:
        if self.launched:
            self.model.step(dt)
            self.model.remove_projectile_if_outside()

    def get_slingshot_line(self, widget_height: int) -> tuple[QPointF, Optional[QPointF]]:
        origin = self._world_to_qt(widget_height, self.model.slingshot_origin)
        if self.dragging and self.model.current_ball is not None:
            pos = self._world_to_qt(widget_height, self.model.current_ball.body.position)
            return origin, pos
        return origin, None

    def get_trajectory(self, widget_height: int) -> list[QPointF]:
        points: list[QPointF] = []
        for x, y in self.model.trajectory:
            points.append(self._world_to_qt(widget_height, pymunk.Vec2d(x, y)))
        return points
