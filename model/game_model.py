import math
from typing import List, Tuple

import pymunk


class GameModel:
    def __init__(self, width: int = 900, height: int = 600) -> None:
        self.width = width
        self.height = height
        self.space = pymunk.Space()
        self.space.gravity = (0, -900)

        self.slingshot_origin = pymunk.Vec2d(150, 180)
        self.projectile_radius = 16
        self.projectile_mass = 4
        self.max_drag_distance = 140

        self.current_ball: pymunk.Circle | None = None
        self.blocks: list[pymunk.Shape] = []
        self.floor: pymunk.Segment | None = None
        self.trajectory: List[Tuple[float, float]] = []
        self._build_world()
        self.reset_projectile()

    def _build_world(self) -> None:
        static_body = self.space.static_body
        ground_height = 60
        self.floor = pymunk.Segment(static_body, (0, ground_height), (self.width, ground_height), 4)
        self.floor.friction = 1.0
        self.space.add(self.floor)

        block_width, block_height = 60, 30
        start_x = 600
        start_y = ground_height + block_height / 2
        rows = 5
        cols = 4
        for row in range(rows):
            for col in range(cols):
                x = start_x + col * (block_width + 5)
                y = start_y + row * (block_height + 2)
                body = pymunk.Body(5, pymunk.moment_for_box(5, (block_width, block_height)))
                body.position = (x, y)
                shape = pymunk.Poly.create_box(body, (block_width, block_height))
                shape.elasticity = 0.2
                shape.friction = 0.8
                self.space.add(body, shape)
                self.blocks.append(shape)

    def reset_projectile(self) -> None:
        if self.current_ball is not None:
            body = self.current_ball.body
            self.space.remove(body, self.current_ball)
        body = pymunk.Body(self.projectile_mass, pymunk.moment_for_circle(self.projectile_mass, 0, self.projectile_radius))
        body.position = self.slingshot_origin
        shape = pymunk.Circle(body, self.projectile_radius)
        shape.elasticity = 0.6
        shape.friction = 0.9
        self.space.add(body, shape)
        self.current_ball = shape
        self.trajectory.clear()

    def clamp_drag_position(self, world_position: pymunk.Vec2d) -> pymunk.Vec2d:
        offset = world_position - self.slingshot_origin
        distance = offset.length
        if distance > self.max_drag_distance:
            offset.length = self.max_drag_distance
        return self.slingshot_origin + offset

    def launch_projectile(self, release_position: pymunk.Vec2d) -> None:
        if self.current_ball is None:
            return
        body = self.current_ball.body
        tension = self.slingshot_origin - release_position
        impulse = tension * 7
        body.velocity = (0, 0)
        body.angular_velocity = 0
        body.apply_impulse_at_local_point(impulse)
        self.trajectory = [(float(body.position.x), float(body.position.y))]

    def append_trajectory_point(self) -> None:
        if self.current_ball is None:
            return
        pos = self.current_ball.body.position
        if not self.trajectory or (pos.x, pos.y) != self.trajectory[-1]:
            self.trajectory.append((float(pos.x), float(pos.y)))

    def step(self, dt: float) -> None:
        self.space.step(dt)
        self.append_trajectory_point()

    def get_shapes(self) -> list[pymunk.Shape]:
        shapes: list[pymunk.Shape] = []
        if self.current_ball is not None:
            shapes.append(self.current_ball)
        shapes.extend(self.blocks)
        if self.floor is not None:
            shapes.append(self.floor)
        return shapes

    def remove_projectile_if_outside(self) -> None:
        if self.current_ball is None:
            return
        pos = self.current_ball.body.position
        if pos.y < -200 or pos.x > self.width * 2:
            self.reset_projectile()

    @staticmethod
    def poly_world_vertices(shape: pymunk.Poly) -> list[pymunk.Vec2d]:
        body = shape.body
        return [body.transform * v for v in shape.get_vertices()]
