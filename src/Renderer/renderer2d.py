import os
import json
import numpy
from Renderer.base_renderer import pygame, SetupOptions, RendererBase


class Camera2D:
    def __init__(self) -> None:
        self.pos: numpy.ndarray = numpy.array([0.0, 0.0])
        self.scale: float = 30
        self.speed: float = 4


class Object2D:
    def __init__(self) -> None:
        self.name: str = ""
        self.pos: numpy.ndarray = numpy.array([0.0, 0.0])
        self.vertices: list[numpy.ndarray] = []
        self.edges: list[numpy.ndarray] = []
        self.colors: dict[str, pygame.Color] = {}
        self.items: list[dict] = []


class Object2DTemplate:
    def __init__(self, obj_params: dict) -> None:
        self.name: str = obj_params["name"]

        self.vertices: list[numpy.ndarray] = [
            numpy.array(vertex) for vertex in obj_params["vertices"]
        ]
        self.edges: list[numpy.ndarray] = [
            numpy.array(edge) for edge in obj_params["edges"]
        ]

        self.colors: dict[str, pygame.Color] = {}
        for color, rgb in obj_params["colors"].items():
            self.colors[color] = pygame.Color(rgb)

        self.items: list[dict] = []
        for item in obj_params["render"]:
            self.items.append(item)

    def create_obj(self, pos: numpy.ndarray) -> Object2D:
        obj = Object2D()
        obj.name = self.name
        obj.pos = pos
        obj.vertices = self.vertices
        obj.edges = self.edges
        obj.colors = self.colors
        obj.items = self.items
        return obj


class Renderer2D(RendererBase):
    def __init__(self, options: SetupOptions) -> None:
        super().__init__(options)
        self._camera: Camera2D = Camera2D()
        self._object_templates: dict[str, Object2DTemplate] = {}
        self._objects: list[Object2D] = []

        self._load_obj_templates()

    def zoom(self, scale: float) -> None:
        self._camera.scale += scale

    def _load_obj_templates(self) -> None:
        objects_path: str = "src/Renderer/data/objects2d"

        for filename in os.listdir(objects_path):
            if filename.endswith(".obj"):
                with open(f"{objects_path}/{filename}", "r") as file:
                    obj: dict = json.load(file)

                    self._object_templates[obj["name"]] = Object2DTemplate(obj)

    def create_object(
        self, obj_name: str, pos: tuple[float, float] | numpy.ndarray
    ) -> None:
        obj = self._object_templates[obj_name].create_obj(numpy.array(pos))
        self._objects.append(obj)

    def _delete_object(self, idx: int) -> None:
        self._objects.pop(idx)

    def update(self, dt: float) -> None:
        keys: pygame.key.ScancodeWrapper = pygame.key.get_pressed()

        cam_speed = (
            self._camera.speed
            * (2 if keys[pygame.K_LCTRL] else 1)
            * (0.5 if keys[pygame.K_LSHIFT] else 1)
            * dt
        )

        delta_x = cam_speed * (keys[pygame.K_d] - keys[pygame.K_a])
        delta_y = cam_speed * (keys[pygame.K_w] - keys[pygame.K_s])

        self._camera.pos[0] += delta_x
        self._camera.pos[1] += delta_y

        if self._debug_mode and self._debug_cursor_idx:
            self._objects[self._debug_cursor_idx].pos = self._camera.pos

            self.create_object("square", self._camera.pos)  # TODO: REMOVE

    def _project_point(self, point: numpy.ndarray) -> tuple[numpy.ndarray, bool]:
        point[1] *= -1
        point *= self._camera.scale
        point += (
            -self._camera.pos[0] * self._camera.scale,
            self._camera.pos[1] * self._camera.scale,
        )
        point += numpy.array([self._win_width // 2, self._win_height // 2])

        tolerance = self._camera.scale * 1

        on_screen = (
            0 - tolerance < point[0] < self._win_width + tolerance
            and 0 - tolerance < point[1] < self._win_height + tolerance
        )

        return point, on_screen

    def _render_point(
        self, point: numpy.ndarray, color: pygame.Color, radius: int = 1
    ) -> bool:
        point, on_screen = self._project_point(point)
        if not on_screen:
            return False

        pygame.draw.circle(self._window, color, tuple(point), radius)
        return True

    def _render_line(
        self,
        point1: numpy.ndarray,
        point2: numpy.ndarray,
        color: pygame.Color,
        width: int = 1,
    ) -> bool:
        point1, on_screen1 = self._project_point(point1)
        if not on_screen1:
            return False

        point2, on_screen2 = self._project_point(point2)
        if not on_screen2:
            return False

        pygame.draw.line(self._window, color, tuple(point1), tuple(point2), width)
        return True

    def _render_object(self, obj: Object2D) -> bool:
        for item in obj.items:
            match item["type"]:
                case "point":
                    drawn = self._render_point(
                        obj.vertices[item["pos"]] + obj.pos,
                        obj.colors[item["color"]],
                        3,
                    )
                    if not drawn:
                        return False
                case "line":
                    start: numpy.ndarray = obj.vertices[obj.edges[item["pos"]][0]]
                    end: numpy.ndarray = obj.vertices[obj.edges[item["pos"]][1]]

                    drawn = self._render_line(
                        start + obj.pos,
                        end + obj.pos,
                        obj.colors[item["color"]],
                    )
                    if not drawn:
                        return False
        return True

    def _render_objects(self) -> None:
        self._current_rendered = 0
        for obj in self._objects:
            self._current_rendered += self._render_object(obj)

        if self._debug_mode:
            self._render_object

    def draw_ui(self) -> None:
        if self._debug_mode:
            debug_text: str = (
                f"FPS: {round(self._clock.get_fps(), 2)}\n"
                + f"Objects (Rendered/Total): {self._current_rendered}/{len(self._objects)}\n"
                + f"Camera Pos: {self._camera.pos}\n"
            )
            for idx, line in enumerate(debug_text.split("\n")):
                line_distance: int = self.fonts["debug"].get_height() + 4
                debug_label: pygame.Surface = self.fonts["debug"].render(
                    line, 1, (255, 255, 255)
                )
                self._window.blit(debug_label, (10, 10 + idx * line_distance))

    def _toggle_debug(self) -> None:
        self._debug_mode = not self._debug_mode
        if self._debug_mode:
            self._debug_cursor_idx = len(self._objects)
            self.create_object("debug_cursor", self._camera.pos)
            self.create_object("origin_cross", (0.0, 0.0))  # TODO: REMOVE
        elif self._debug_cursor_idx:
            self._delete_object(self._debug_cursor_idx)
            self._delete_object(self._debug_cursor_idx)  # TODO: REMOVE
            self._debug_cursor_idx = None
