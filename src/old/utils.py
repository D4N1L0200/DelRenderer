from typing import Self
import math
import numpy as np


class Position:
    def __init__(self, x: float, y: float, z: float) -> None:
        self.x: float = x
        self.y: float = y
        self.z: float = z

    def get_nparray_v3(self) -> np.array:
        return np.array([self.x, self.y, self.z])

    def get_nparray_v2(self) -> np.array:
        return np.array([self.x, self.y])

    def __add__(self, other: float) -> Self:
        if isinstance(other, float):
            return Position(self.x + other, self.y + other, self.z + other)

    def __sub__(self, other: float) -> Self:
        if isinstance(other, float):
            return Position(self.x - other, self.y - other, self.z - other)

    def __mul__(self, other: float) -> Self:
        if isinstance(other, float):
            return Position(self.x * other, self.y * other, self.z * other)

    def __round__(self, n: int = 0) -> Self:
        return Position(round(self.x, n), round(self.y, n), round(self.z, n))

    def __str__(self) -> str:
        return f"({self.x}, {self.y}, {self.z})"

    def __repr__(self) -> str:
        return f"Position({self.x}, {self.y}, {self.z})"

    def move(self, length: float, direction: np.array) -> Self:
        magnitude = math.sqrt(sum(x**2 for x in direction))
        normalized_direction = [x / magnitude for x in direction]

        new_position = [
            self.x + normalized_direction[0] * length,
            self.y + normalized_direction[1] * length,
            self.z + normalized_direction[2] * length,
        ]

        return Position(*new_position)


class Rotation:
    def __init__(self, yaw: float, pitch: float) -> None:
        self.yaw: float = yaw
        self.pitch: float = pitch

    def get_vector(self) -> np.array:
        return np.clip(
            np.array(
                [
                    np.sin(self.yaw) * np.cos(self.pitch),
                    np.sin(self.pitch),
                    np.cos(self.yaw) * np.cos(self.pitch),
                ]
            ),
            -1,
            1,
        )

    def __round__(self, n: int = 0) -> Self:
        yaw = round(self.yaw, n)
        if yaw > math.pi:
            yaw -= math.pi * 2
        elif yaw < -math.pi:
            yaw += math.pi * 2
        pitch = min(max(round(self.pitch, n), -math.pi / 2), math.pi / 2)
        return Rotation(yaw, pitch)

    def __str__(self) -> str:
        return f"({self.yaw}, {self.pitch})"

    def __repr__(self) -> str:
        return f"Rotation({self.yaw}, {self.pitch})"


class Camera:
    def __init__(self) -> None:
        self.pos: Position = Position(0, 0, 0)
        self.rot: Rotation = Rotation(0, 0)
        self.near_plane: float = 1e-5
        self.far_plane: int = 20
        self.depth_scaling: int = 200
        self.speed_3d: float = 0.1
        self.speed_2d: float = 2
        self.sens: float = 0.02


class RenderMode:
    R3D: int = 0b1
    R2D: int = 0b10
    R3DW: int = 0b100
