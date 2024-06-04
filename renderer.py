import pygame
import numpy as np
from typing import Union
from utils import Camera
from objects import ObjectTemplate, Object
import math
import json
import os


class Renderer:
    def __init__(
        self, size: tuple[int, int] = (0, 0), mode: str = "3DWireframe"
    ) -> None:
        flags: int = (
            pygame.FULLSCREEN if tuple == (0, 0) else pygame.RESIZABLE
        ) | pygame.DOUBLEBUF
        self.window: pygame.Surface = pygame.display.set_mode(size, flags, 8)
        pygame.init()
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.VIDEORESIZE])
        pygame.display.set_caption("DelRenderer")
        pygame.mouse.set_visible(False)
        info = pygame.display.Info()
        self.win_width, self.win_height = (
            info.current_w,
            info.current_h,
        )
        pygame.mouse.set_pos(self.win_width // 2, self.win_height // 2)
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.settings: dict = {}
        self.camera: Camera = Camera()
        self.mouse_locked: bool = True
        self.debug_mode: bool = False
        self.fonts: dict[str, pygame.font.Font] = {
            "default": pygame.font.Font(None, 24),
            "debug": pygame.font.SysFont("monospace", 28),
        }
        self.mode: str = mode
        self.object_templates: dict[str, ObjectTemplate] = {}
        self.objects: list[Object] = []

    def load_settings(self) -> None:
        with open("settings.json", "r") as file:
            settings = json.load(file)

            self.settings = settings

            self.camera.near_plane = settings["camera"]["near_plane"]
            self.camera.far_plane = settings["camera"]["far_plane"]
            self.camera.depth_scaling = settings["camera"]["depth_scaling"]
            self.camera.speed_2d = settings["camera"]["speed_2d"]
            self.camera.speed_3d = settings["camera"]["speed_3d"]
            self.camera.sens = settings["camera"]["sens"]

    def load_obj_templates(self) -> None:
        objects_path: str = self.settings["file_paths"]["objects"]

        for filename in os.listdir(objects_path):
            if filename.endswith(".obj"):
                with open(f"{objects_path}/{filename}", "r") as file:
                    obj: dict = json.load(file)

                    self.object_templates[obj["name"]] = ObjectTemplate(obj)

    def create_obj(self, obj_name: str, pos: np.array) -> None:
        obj = self.object_templates[obj_name].create_obj(pos)
        self.objects.append(obj)

    def process_inputs(
        self, keys: pygame.key.ScancodeWrapper, mouse_rel: tuple[int, int]
    ) -> None:
        match self.mode:
            case "3DWireframe":
                delta_x = self.camera.speed_3d * (
                    keys[pygame.K_w] - keys[pygame.K_s]
                ) * math.sin(self.camera.rot.yaw) - self.camera.speed_3d * (
                    keys[pygame.K_a] - keys[pygame.K_d]
                ) * math.cos(
                    self.camera.rot.yaw
                )
                delta_z = self.camera.speed_3d * (
                    keys[pygame.K_w] - keys[pygame.K_s]
                ) * math.cos(self.camera.rot.yaw) + self.camera.speed_3d * (
                    keys[pygame.K_a] - keys[pygame.K_d]
                ) * math.sin(
                    self.camera.rot.yaw
                )

                self.camera.pos.x += delta_x
                self.camera.pos.z += delta_z
                self.camera.pos.y += (
                    keys[pygame.K_SPACE] - keys[pygame.K_LSHIFT]
                ) * self.camera.speed_3d
                self.camera.pos = round(self.camera.pos, 4)

                mouse_dx, mouse_dy = mouse_rel
                self.camera.rot.yaw += mouse_dx * self.camera.sens
                self.camera.rot.pitch -= mouse_dy * self.camera.sens
                self.camera.rot = round(self.camera.rot, 4)
            case "2D":
                cam_speed = self.camera.speed_2d + (keys[pygame.K_LSHIFT] * 4)
                delta_x = cam_speed * (keys[pygame.K_d] - keys[pygame.K_a])
                delta_y = cam_speed * (keys[pygame.K_w] - keys[pygame.K_s])

                self.camera.pos.x += delta_x
                self.camera.pos.y += delta_y
                self.camera.pos = round(self.camera.pos, 4)

    def project_3d_point(self, point: np.array) -> Union[np.array, None]:
        x, y, z = point
        x -= self.camera.pos.x
        y -= self.camera.pos.y
        z -= self.camera.pos.z

        x, z = x * np.cos(self.camera.rot.yaw) - z * np.sin(
            self.camera.rot.yaw
        ), x * np.sin(self.camera.rot.yaw) + z * np.cos(self.camera.rot.yaw)
        y, z = y * np.cos(self.camera.rot.pitch) - z * np.sin(
            self.camera.rot.pitch
        ), y * np.sin(self.camera.rot.pitch) + z * np.cos(self.camera.rot.pitch)

        epsilon = 1e-5
        z += epsilon

        if z < self.camera.near_plane:
            return None

        if z > self.camera.far_plane:
            return None

        f = self.camera.depth_scaling / z
        x, y = x * f, y * f
        return np.array([self.win_width / 2 + x, self.win_height / 2 - y])

    def render_3d_point(
        self, point: np.array, color: tuple[int, int, int], radius: int = 1
    ) -> bool:
        pos = self.project_3d_point(point)
        if isinstance(pos, np.ndarray):
            pygame.draw.circle(self.window, color, pos, radius)
            return True
        return False

    def render_3d_line(
        self,
        point1: np.array,
        point2: np.array,
        color: tuple[int, int, int],
        width: int = 1,
    ) -> bool:
        # def calc_intersect(
        #     point1: tuple[int, int, int], point2: tuple[int, int, int]
        # ) -> tuple[int, int, int]:
        #     return point1

        pos1 = self.project_3d_point(point1)
        pos2 = self.project_3d_point(point2)
        if isinstance(pos1, np.ndarray) and isinstance(pos2, np.ndarray):
            pygame.draw.line(self.window, color, pos1, pos2, width)
            return True
        return False
        # if pos1 or pos2:
        #     if not pos1:
        #         pos1 = calc_intersect(point1, point2)
        #         pygame.draw.line(self.window, color, pos1, pos2, 1)
        #     if not pos2:
        #         pos2 = calc_intersect(point1, point2)
        #         pygame.draw.line(self.window, color, pos1, pos2, 1)

    def render_3d_object(self, obj: Object) -> bool:
        for item in obj.items:
            match item["type"]:
                case "point":
                    self.render_3d_point(
                        obj.vertices[item["pos"]] + obj.pos,
                        obj.colors[item["color"]],
                        3,
                    )
                case "line":
                    start: np.array = obj.vertices[obj.edges[item["pos"]][0]]
                    end: np.array = obj.vertices[obj.edges[item["pos"]][1]]

                    self.render_3d_line(
                        start + obj.pos,
                        end + obj.pos,
                        obj.colors[item["color"]],
                    )
        return True

        # elif object_name == "debug_cursor":
        #     x: np.array = pos + (0.3, 0, 0)
        #     y: np.array = pos + (0, 0.3, 0)
        #     z: np.array = pos + (0, 0, 0.3)
        #
        #     self.render_3d_line(pos, x, (255, 0, 0))
        #     self.render_3d_line(pos, y, (0, 255, 0))
        #     self.render_3d_line(pos, z, (0, 0, 255))
        # elif object_name == "origin_cross":
        #     c: tuple[int, int, int] = (255, 255, 255)
        #     for i in range(-10, 11):
        #         self.render_3d_line(pos, pos + (i, 0, 0), c)
        #         self.render_3d_line(pos, pos + (0, i, 0), c)
        #         self.render_3d_line(pos, pos + (0, 0, i), c)
        # elif object_name == "floor_grid":
        #     c: tuple[int, int, int] = (255, 255, 255)
        #     radius: int = 10
        #     for x in range(-radius, radius):
        #         for z in range(-radius, radius):
        #             offset = (x, 0, z)
        #             self.render_3d_line(pos + offset, pos + offset + (1, 0, 0), c)
        #             self.render_3d_line(pos + offset, pos + offset + (0, 0, 1), c)
        #             if x == radius - 1:
        #                 self.render_3d_line(
        #                     pos + offset + (1, 0, 0), pos + offset + (1, 0, 1), c
        #                 )
        #             if z == radius - 1:
        #                 self.render_3d_line(
        #                     pos + offset + (0, 0, 1), pos + offset + (1, 0, 1), c
        #                 )

    # for i in range(len(self.vertices) - 1):
    #     self.render_line(self.vertices[i], self.vertices[i + 1])

    def render_objects_3d(self) -> None:
        # with Pool(processes=1) as pool:
        #     results = pool.map(self.render_3d_object, self.objects)
        # print(results)
        for obj in self.objects:
            self.render_3d_object(obj)

    def project_2d_point(self, point: np.array) -> Union[np.array, None]:
        x = point[0] - self.camera.pos.x + self.win_width / 2
        y = -point[1] + self.camera.pos.y + self.win_height / 2
        if x < 0 or x > self.win_width or y < 0 or y > self.win_height:
            return None
        return np.array([x, y])

    def render_2d_point(
        self, point: np.array, color: tuple[int, int, int], radius: int = 1
    ) -> bool:
        pos = self.project_2d_point(point)
        if isinstance(pos, np.ndarray):
            pygame.draw.circle(self.window, color, pos, radius)
            return True
        return False

    def render_objects_2d(self) -> None:
        # for x in range(-60, 61):
        #     for y in range(-60, 61):
        #         cx = abs(int(255 * x / 60))
        #         cy = abs(int(255 * y / 60))
        #         cxy = abs(int(255 * (x + y) / 120))
        #         c = (cx, cy, cxy)
        #         self.render_2d_point(np.array([x * 5, y * 5]), c, 3)

        for x in range(-30, 31):
            for y in range(-30, 31):
                cx = abs(int(255 * x / 30))
                cy = abs(int(255 * y / 30))
                cxy = abs(int(255 * (x + y) / 60))
                c = (cx, cy, cxy)
                self.render_2d_point(np.array([x * 50, y * 50]), c, 3)

    def start(self) -> None:
        self.load_settings()
        self.load_obj_templates()

        self.create_obj("origin_cross", np.array([0, 0, 0]))
        # self.create_obj("cube", np.array([1, 1, 1]))

        # radius = 10
        # for x in range(1)

        running: bool = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.mouse_locked = not self.mouse_locked
                        pygame.mouse.get_rel()
                    elif event.key == pygame.K_F1:
                        self.debug_mode = not self.debug_mode
                    elif event.key == pygame.K_r:
                        self.load_settings()
                if event.type == pygame.VIDEORESIZE:
                    self.win_width = event.w
                    self.win_height = event.h

            if self.mouse_locked:
                self.process_inputs(pygame.key.get_pressed(), pygame.mouse.get_rel())
                pygame.mouse.set_pos(self.win_width // 2, self.win_height // 2)

            self.window.fill(0)

            # self.render_object("origin_cross", np.array([0, 0, 0]))
            # self.render_3d_object("floor_grid", np.array([0, 0, 0]))
            # self.render_3d_object("origin", np.array([0, 0, 0]))
            # self.render_object("cube", np.array([2, 0, 0]))

            match self.mode:
                case "3DWireframe":
                    self.render_objects_3d()
                case "2D":
                    self.render_objects_2d()

            if self.debug_mode:
                if len(self.objects) < 200:
                    self.create_obj(
                        "cube",
                        self.camera.pos.move(
                            2, self.camera.rot.get_vector()
                        ).get_nparray_v3(),
                    )

                debug_text: str = (
                    f"FPS: {round(self.clock.get_fps(), 2)}\n"
                    + f"Object ammount: {len(self.objects)}\n"
                    + f"Camera Pos: {self.camera.pos}\n"
                    + f"Camera Rot: {self.camera.rot}\n"
                )
                for idx, line in enumerate(debug_text.split("\n")):
                    line_distance: int = self.fonts["debug"].get_height() + 4
                    debug_label: pygame.Surface = self.fonts["debug"].render(
                        line, 1, (255, 255, 255)
                    )
                    self.window.blit(debug_label, (10, 10 + idx * line_distance))
            else:
                if self.mouse_locked:
                    pygame.draw.circle(
                        self.window,
                        (255, 255, 255),
                        (self.win_width / 2, self.win_height / 2),
                        2,
                    )

            if not self.mouse_locked:
                pygame.draw.circle(
                    self.window,
                    (255, 255, 255),
                    pygame.mouse.get_pos(),
                    2,
                )

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
