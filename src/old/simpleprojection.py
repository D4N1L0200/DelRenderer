import pygame
import math
import numpy as np
from typing import Self


class Position:
    def __init__(self, x: float, y: float, z: float) -> None:
        self.x: float = x
        self.y: float = y
        self.z: float = z

    def get_nparray(self) -> np.array:
        return np.array([self.x, self.y, self.z])

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

    def __repr__(self) -> str:
        return f"({self.x}, {self.y}, {self.z})"


class Rotation:
    def __init__(self, yaw: float, pitch: float) -> None:
        self.yaw: float = yaw
        self.pitch: float = pitch

    def get_vector(self) -> np.array:  # TODO: INVERT
        return np.clip(
            np.array(
                [
                    np.cos(self.yaw) * np.cos(self.pitch),
                    np.sin(self.yaw) * np.cos(self.pitch),
                    np.sin(self.pitch),
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

    def __repr__(self) -> str:
        return f"({self.yaw}, {self.pitch})"


class Player:
    def __init__(self) -> None:
        self.cam_pos: Position = Position(0, 0, 0)
        self.cam_rot: Rotation = Rotation(0, 0)
        self.cam_speed: float = 0.1
        self.cam_sens: float = 0.02


class Renderer:
    def __init__(self, world: np.array, size: tuple[int, int] = (0, 0)) -> None:
        self.world: np.array = world
        self.window: pygame.Surface = pygame.display.set_mode(
            size, pygame.FULLSCREEN if tuple == (0, 0) else pygame.RESIZABLE
        )
        pygame.display.set_caption("Renderer")
        pygame.mouse.set_visible(False)
        info = pygame.display.Info()
        self.win_width, self.win_height = (
            info.current_w,
            info.current_h,
        )
        pygame.mouse.set_pos(self.win_width // 2, self.win_height // 2)
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.player: Player = Player()
        self.mouse_locked: bool = True

    def process_inputs(self, keys: pygame.key.ScancodeWrapper) -> None:
        delta_x = self.player.cam_speed * (
                keys[pygame.K_w] - keys[pygame.K_s]
        ) * math.sin(self.player.cam_rot.yaw) - self.player.cam_speed * (
                          keys[pygame.K_a] - keys[pygame.K_d]
                  ) * math.cos(
            self.player.cam_rot.yaw
        )
        delta_z = self.player.cam_speed * (
                keys[pygame.K_w] - keys[pygame.K_s]
        ) * math.cos(self.player.cam_rot.yaw) + self.player.cam_speed * (
                          keys[pygame.K_a] - keys[pygame.K_d]
                  ) * math.sin(
            self.player.cam_rot.yaw
        )

        self.player.cam_pos.x += delta_x
        self.player.cam_pos.z += delta_z
        self.player.cam_pos.y += (
                                         keys[pygame.K_SPACE] - keys[pygame.K_LSHIFT]
                                 ) * self.player.cam_speed
        self.player.cam_pos = round(self.player.cam_pos, 4)

        mouse_dx, mouse_dy = pygame.mouse.get_rel()
        self.player.cam_rot.yaw += mouse_dx * self.player.cam_sens
        self.player.cam_rot.pitch -= mouse_dy * self.player.cam_sens
        self.player.cam_rot = round(self.player.cam_rot, 4)

    def render_block(
            self, block_x: int, block_y: int, block_z: int, block_id: int
    ) -> None:
        vertices = [
            (0, 0, 0),
            (1, 0, 0),
            (1, 1, 0),
            (0, 1, 0),
            (0, 0, 1),
            (1, 0, 1),
            (1, 1, 1),
            (0, 1, 1),
        ]

        triangles = [
            (0, 2, 1),
            (0, 1, 5),
            (0, 3, 2),
            (0, 7, 3),
            (0, 5, 4),
            (0, 4, 7),
            (1, 2, 5),
            (2, 3, 7),
            (2, 6, 5),
            (2, 7, 6),
            (4, 5, 7),
            (5, 6, 7),
        ]

        def project(p):
            x, y, z = p
            x -= self.player.cam_pos.x
            y -= self.player.cam_pos.y
            z -= self.player.cam_pos.z

            x, z = x * np.cos(self.player.cam_rot.yaw) - z * np.sin(
                self.player.cam_rot.yaw
            ), x * np.sin(self.player.cam_rot.yaw) + z * np.cos(self.player.cam_rot.yaw)
            y, z = y * np.cos(self.player.cam_rot.pitch) - z * np.sin(
                self.player.cam_rot.pitch
            ), y * np.sin(self.player.cam_rot.pitch) + z * np.cos(
                self.player.cam_rot.pitch
            )

            epsilon = 1e-5
            z += epsilon

            f = 200 / z
            x, y = x * f, y * f
            return self.win_width / 2 + x, self.win_height / 2 - y

        proj_vertices = [
            project((v[0] + block_x, v[1] + block_y, v[2] + block_z)) for v in vertices
        ]

        match block_id:
            case 0:
                color = (255, 0, 0)
            case 1:
                color = (255, 255, 255)
            case _:
                color = (255, 0, 255)

        for triangle in triangles:
            # poly = [np.array(vertices[i]) for i in triangle]
            proj_poly = [np.array(proj_vertices[i]) for i in triangle]
            # normal = np.cross((poly[1] - poly[0]), (poly[2] - poly[0]))
            #
            # direction_vector = np.array(
            #     [
            #         np.sin(
            #             self.player.cam_rot.yaw,
            #         )
            #         * np.cos(self.player.cam_rot.pitch),
            #         np.sin(self.player.cam_rot.pitch),
            #         np.cos(
            #             self.player.cam_rot.yaw,
            #         )
            #         * np.cos(self.player.cam_rot.pitch),
            #     ]
            # )
            #
            # normal = normal / np.linalg.norm(normal)
            #
            # if np.dot(normal, direction_vector) < 0:
            pygame.draw.polygon(self.window, color, proj_poly, 1)

    def draw_world(self) -> None:
        # camera_direction = np.array(
        #     [
        #         np.cos(self.player.cam_rot.yaw) * np.cos(self.player.cam_rot.pitch),
        #         np.sin(self.player.cam_rot.pitch),
        #         np.sin(self.player.cam_rot.yaw) * np.cos(self.player.cam_rot.pitch),
        #     ]
        # )
        #
        # camera_direction_end = self.player.cam_pos + camera_direction * 2
        # pygame.draw.line(
        #     self.window,
        #     (255, 0, 0),
        #     (self.player.cam_pos.x, self.player.cam_pos.y),  # TODO
        #     camera_direction_end[:2],
        #     2,
        # )

        for chunk_z in range(self.world.shape[0]):
            for chunk_y in range(self.world.shape[1]):
                for chunk_x in range(self.world.shape[2]):
                    chunk = self.world[chunk_z, chunk_y, chunk_x]

                    for z in range(chunk.shape[0]):
                        for y in range(chunk.shape[1]):
                            for x in range(chunk.shape[2]):
                                block_id = chunk[z, y, x]

                                world_x = chunk_x * chunk.shape[2] + x
                                world_y = chunk_y * chunk.shape[1] + y
                                world_z = chunk_z * chunk.shape[0] + z

                                # block_center = np.array([world_x, world_y, world_z])
                                # vector_to_block = (
                                #     block_center - self.player.cam_pos.get_nparray()
                                # )
                                #
                                # dot_product = np.dot(vector_to_block, camera_direction)
                                #
                                # if dot_product > 0:
                                self.render_block(world_x, world_y, world_z, block_id)
                                # else:
                                #     self.render_block(world_x, world_y, world_z, -1)

    # def draw_world(self) -> None:
    #     for chunk_z in range(self.world.shape[0]):
    #         for chunk_y in range(self.world.shape[1]):
    #             for chunk_x in range(self.world.shape[2]):
    #                 chunk = self.world[chunk_z, chunk_y, chunk_x]
    #
    #                 for z in range(chunk.shape[0]):
    #                     for y in range(chunk.shape[1]):
    #                         for x in range(chunk.shape[2]):
    #                             block_id = chunk[z, y, x]
    #
    #                             world_x = chunk_x * chunk.shape[2] + x
    #                             world_y = chunk_y * chunk.shape[1] + y
    #                             world_z = chunk_z * chunk.shape[0] + z
    #
    #                             self.render_block(world_x, world_y, world_z, block_id)

    def start(self) -> None:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.mouse_locked = not self.mouse_locked
                        pygame.mouse.set_visible(not self.mouse_locked)
                        pygame.mouse.get_rel()
                if event.type == pygame.VIDEORESIZE:
                    self.win_width = event.w
                    self.win_height = event.h

            if self.mouse_locked:
                self.process_inputs(pygame.key.get_pressed())
                pygame.mouse.set_pos(self.win_width // 2, self.win_height // 2)

            self.window.fill(0)

            self.draw_world()

            pygame.draw.circle(
                self.window,
                (255, 255, 255),
                (self.win_width / 2, self.win_height / 2),
                2,
            )

            pygame.display.flip()
            pygame.display.set_caption(
                f"Renderer - FPS: {round(self.clock.get_fps(), 2)}"
            )
            self.clock.tick(60)

        pygame.quit()


pygame.init()

# empty_chunk: np.array = np.array(
#     [[[0 for _ in range(4)] for _ in range(4)] for _ in range(4)]
# )
# overworld = np.array(
#     [[[empty_chunk.copy() for _ in range(2)] for _ in range(2)] for _ in range(2)]
# )

# (len z, len y, len x, size z, size y, size x)
overworld: np.array = np.ones((1, 1, 1, 4, 4, 4), dtype=int)
# overworld: np.array = np.ones((4, 1, 4, 4, 4, 4), dtype=int)
# for idxlz, a in enumerate(overworld):
#     for idxly, b in enumerate(a):
#         for idxlx, c in enumerate(b):
#             for idxsz, d in enumerate(c):
#                 for idxsy, e in enumerate(d):
#                     for idxsx, _ in enumerate(e):
#                         overworld[idxlz, -1, idxlx, idxsz, 3, idxsx] = 2

renderer: Renderer = Renderer(overworld, (800, 600))
renderer.start()

# def get_mouse_pos():
#     x, y = pygame.mouse.get_pos()
#     if ((x % (padding + cell_size)) - padding < 0) or (
#         (y % (padding + cell_size)) - padding < 0
#     ):
#         return -1, -1
#     row = y // (padding + cell_size)
#     col = x // (padding + cell_size)
#     return col, row

# if pygame.mouse.get_pressed()[0]:  # Left Click
#     pass  # sim.add_cell("Grass", get_mouse_pos())
# if pygame.mouse.get_pressed()[2]:  # Right Click
#     pass  # sim.add_cell("Fire", get_mouse_pos())

# self.rotate("x", 45 / 60)
# self.rotate("x", 0.005)
# self.rotate("y", 0.001)

# for idx, point in enumerate(self.world.points.copy()):
#     x, y, z = point
#     degree = 45 * math.pi / 180
#     temp_points = (
#         x * math.cos(degree) - y * math.sin(degree),
#         x * math.sin(degree) + y * math.cos(degree),
#         z,
#     )
#     degree = 45 * math.pi / 180
#     x, y, z = temp_points
#     self.world.points.append(
#         (
#             x,
#             y * math.cos(degree) - z * math.sin(degree),
#             y * math.sin(degree) + z * math.cos(degree),
#         )
#     )
#
# for line in self.world.lines.copy():
#     self.world.lines.append((line[0] + 8, line[1] + 8))

# class Block:
#     def __init__(
#         self, cords: tuple[int, int, int], color: tuple[int, int, int], blockid: int = 0
#     ) -> None:
#         self.id: int = blockid
#         self.cords: tuple[int, int, int] = cords
#         self.color: tuple[int, int, int] = color  # TEMP

# class Chunk:
#     def __init__(self) -> None:
#         self.blockgrid: list[*list[*list[Block]]] | None = None
#
#     def create(self, x, y, z) -> None:
#         self.blockgrid = [
#             [
#                 [
#                     # Block((bx, by, bz), color=(bx * 100, by * 100, bz * 100))
#                     # Block((bx, by, bz), color=(bx * 25, by * 25, bz * 25))
#                     Block((bx, by, bz), color=(bx * 20, by * 20, bz * 20))
#                     for bx in range(x)
#                 ]
#                 for bz in range(z)
#             ]
#             for by in range(y)
#         ]
#
#     #
#     # def getblocks(self) -> list[Block]:

# class World:
#     def __init__(self) -> None:
#         temp_chunk = Chunk()
#         # temp_chunk.create(2, 2, 2)
#         # temp_chunk.create(8, 8, 8)
#         temp_chunk.create(10, 10, 10)
#         self.chunks: list[Chunk] = [temp_chunk]
#         # self.points: list[tuple[int, int, int]] = [(0, 0, 0)]
#         # self.lines: list[tuple[int, int]] = [(0, 0)]

# def rotate(
#     self, axis: str, angle_deg: int, points: list[tuple[float, float, float]]
# ) -> list[tuple[float, float, float]]:
#     angle_rad = angle_deg * math.pi / 180
#     if axis == "x":
#         rotation_matrix = np.array(
#             [
#                 [1, 0, 0],
#                 [0, np.cos(angle_rad), -np.sin(angle_rad)],
#                 [0, np.sin(angle_rad), np.cos(angle_rad)],
#             ]
#         )
#     elif axis == "y":
#         rotation_matrix = np.array(
#             [
#                 [np.cos(angle_rad), 0, np.sin(angle_rad)],
#                 [0, 1, 0],
#                 [-np.sin(angle_rad), 0, np.cos(angle_rad)],
#             ]
#         )
#     elif axis == "z":
#         rotation_matrix = np.array(
#             [
#                 [np.cos(angle_rad), -np.sin(angle_rad), 0],
#                 [np.sin(angle_rad), np.cos(angle_rad), 0],
#                 [0, 0, 1],
#             ]
#         )
#     else:
#         return points
#     for idx, point in enumerate(points):
#         points[idx] = np.dot(rotation_matrix, point)
#     return points

# def draw_points(self, points: list[tuple[float, float]]) -> None:
#     for point in points:
#         pygame.draw.circle(
#             self.window,
#             (255, 255, 255),
#             point,
#             5,
#         )

# def draw_lines(
#     self,
#     points: list[tuple[float, float]],
#     lines: list[tuple[int, int]],
#     color: tuple[int, int, int] = (255, 255, 255),
# ) -> None:
#     for line in lines:
#         pygame.draw.line(
#             self.window,
#             color,
#             points[line[0] - 1],
#             points[line[1] - 1],
#             2,
#         )

# def draw_block(self, block: Block, scale: int = 1, angle=0) -> None:
#     def project_points(
#         points: list[tuple[int, int, int]]
#     ) -> list[tuple[float, float]]:
#         def getproj(xyz: tuple[int, int, int], focal_lenght: int, scale: float):
#             x, y, z = xyz
#             x_proj = (focal_lenght * x) / (focal_lenght + z)
#             y_proj = (focal_lenght * y) / (focal_lenght + z)
#             return (x_proj * scale + self.win_width / 2), (
#                 y_proj * scale + self.win_height / 2
#             )
#
#         proj_points = []
#         for point in points:
#             proj_point = getproj(point, 50, scale)
#             proj_points.append(proj_point)
#         return proj_points
#
#     block_points = [
#         (1, 1, 1),
#         (1, 0, 1),
#         (0, 1, 1),
#         (0, 0, 1),
#         (1, 1, 0),
#         (1, 0, 0),
#         (0, 1, 0),
#         (0, 0, 0),
#     ]
#     block_lines = [
#         (1, 2),
#         (1, 3),
#         (2, 4),
#         (3, 4),
#         (5, 6),
#         (5, 7),
#         (6, 8),
#         (7, 8),
#         (1, 5),
#         (2, 6),
#         (3, 7),
#         (4, 8),
#         # (1, 4),
#         # (4, 7),
#         # (4, 6),
#         # (1, 7),
#         # (1, 6),
#         # (6, 7),
#     ]
#     x, y, z = block.cords
#     # x += self.camera.x
#     # y += self.camera.y
#     # z += self.camera.z
#     block_points = [
#         (block_points[i][0] + x, block_points[i][1] + y, block_points[i][2] + z)
#         for i in range(8)
#     ]
#     # input(f"{x}, {y}, {z}, {block_points}")
#     block_points = self.rotate("x", angle, block_points)
#     block_points = self.rotate("y", angle / 2, block_points)
#     # block_points = self.rotate("x", 10, block_points)
#     proj_points: list[tuple[float, float]] = project_points(block_points)
#     # self.draw_points(proj_points)
#     self.draw_lines(proj_points, block_lines, block.color)

# def draw_world(self, angle) -> None:
#     for chunk in self.world.chunks:
#         for layer in chunk.blockgrid:
#             for row in layer:
#                 for block in row:
#                     self.draw_block(block, scale=50, angle=angle)
