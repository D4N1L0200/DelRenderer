import os
import json
from Renderer.base_renderer import pygame, numpy, SetupOptions, RendererBase
from typing import Callable


class Camera2D:
    def __init__(self) -> None:
        self.pos: numpy.ndarray = numpy.array([0.0, 0.0])
        self.scale: float = 30.0
        self.sens: float = 1.0


class Object2D:
    def __init__(self) -> None:
        self.name: str = ""
        self.pos: numpy.ndarray = numpy.array([0.0, 0.0])
        self.vertices: list[numpy.ndarray] = []
        self.edges: list[numpy.ndarray] = []
        self.colors: dict[str, pygame.Color] = {}
        self.items: list[dict] = []
        self.bounds: numpy.ndarray = numpy.array([0.0, 0.0, 0.0, 0.0], dtype=float)

    def calc_bounds(self, project_point: Callable) -> None:
        min_point = numpy.array([numpy.inf, numpy.inf], dtype=float)
        max_point = numpy.array([-numpy.inf, -numpy.inf], dtype=float)

        for vertice in self.vertices:
            min_point[0] = min(min_point[0], vertice[0])
            min_point[1] = min(min_point[1], vertice[1])
            max_point[0] = max(max_point[0], vertice[0])
            max_point[1] = max(max_point[1], vertice[1])

        min_point += self.pos
        max_point += self.pos

        self.bounds = numpy.array(
            [
                (min_point[0]),
                (min_point[1]),
                (max_point[0] - min_point[0]),
                (max_point[1] - min_point[1]),
            ],
            dtype=float,
        )


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

        self._screen_bounds: numpy.ndarray = numpy.array(
            [
                0,
                0,
                self._win_width,
                self._win_height,
            ],
            dtype=float,
        )

        self._load_obj_templates()

        self.create_object("origin_cross", (0.0, 0.0))

    def _resize(self, width: int, height: int) -> None:
        super()._resize(width, height)
        self._screen_bounds[2] = width
        self._screen_bounds[3] = height

    def mouse_pressed(self, pos: tuple[int, int], button: int) -> None:
        if button == pygame.BUTTON_LEFT:
            self.create_object("square", self._camera.pos - (0.5, 0.5))
        elif button == pygame.BUTTON_MIDDLE:
            self._middle_clicked = True
        elif button == pygame.BUTTON_WHEELUP:
            self.zoom(5)
        elif button == pygame.BUTTON_WHEELDOWN:
            self.zoom(-5)

    def mouse_released(self, pos: tuple[int, int], button: int) -> None:
        if button == pygame.BUTTON_MIDDLE:
            self._middle_clicked = False
            self._last_mouse_pos = None

    def zoom(self, scale: float) -> None:
        self._camera.scale += scale
        self._camera.scale = max(self._camera.scale, 1)

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
        obj = self._object_templates[obj_name].create_obj(numpy.array(pos, dtype=float))
        obj.calc_bounds(self._project_point)
        self._objects.append(obj)

    def _delete_object(self, idx: int) -> None:
        self._objects.pop(idx)

    def update(self, dt: float) -> None:
        if self._middle_clicked:
            mouse_pos: numpy.ndarray = numpy.array(pygame.mouse.get_pos(), dtype=float)
            if self._last_mouse_pos is not None:
                offset: float = dt * 60 / self._camera.scale * self._camera.sens
                self._camera.pos[0] += (self._last_mouse_pos[0] - mouse_pos[0]) * offset
                self._camera.pos[1] -= (self._last_mouse_pos[1] - mouse_pos[1]) * offset
            self._last_mouse_pos = mouse_pos

        if self._debug_mode and self._debug_cursor_idx:
            self._objects[self._debug_cursor_idx].pos = self._camera.pos

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

    def _project_rect(self, rect: numpy.ndarray) -> tuple[float, float, float, float]:
        point, _ = self._project_point(numpy.array([rect[0], rect[1]], dtype=float))
        width, height = rect[2] * self._camera.scale, rect[3] * self._camera.scale
        return point[0], point[1] - height, width, height

    def _render_point(
        self, point: numpy.ndarray, color: pygame.Color, radius: int = 1
    ) -> bool:
        point, on_screen = self._project_point(point)

        if on_screen:
            pygame.draw.circle(self._window, color, tuple(point), radius)
            return True
        return False

    def _render_line(
        self,
        point1: numpy.ndarray,
        point2: numpy.ndarray,
        color: pygame.Color,
        width: int = 1,
    ) -> bool:
        point1, on_screen1 = self._project_point(point1)
        point2, on_screen2 = self._project_point(point2)

        if on_screen1 and on_screen2:
            pygame.draw.line(self._window, color, tuple(point1), tuple(point2), width)
            return True
        return False

    def _is_object_showing(self, obj: Object2D) -> bool:
        x1, y1, w1, h1 = self._project_rect(obj.bounds)
        x2, y2, w2, h2 = self._screen_bounds

        x_overlap = not (x1 + w1 < x2 or x2 + w2 < x1)
        y_overlap = not (y1 + h1 < y2 or y2 + h2 < y1)

        return x_overlap and y_overlap

    def _render_object(self, obj: Object2D) -> bool:
        if not self._is_object_showing(obj):
            return False

        for item in obj.items:
            if item["type"] == "point":
                self._render_point(
                    obj.vertices[item["pos"]] + obj.pos,
                    obj.colors[item["color"]],
                    3,
                )
            elif item["type"] == "line":
                start: numpy.ndarray = obj.vertices[obj.edges[item["pos"]][0]]
                end: numpy.ndarray = obj.vertices[obj.edges[item["pos"]][1]]

                self._render_line(
                    start + obj.pos,
                    end + obj.pos,
                    obj.colors[item["color"]],
                )
        return True

    def _render_objects(self) -> None:
        self._current_rendered = 0
        for obj in self._objects:
            self._current_rendered += self._render_object(obj)

        if self._debug_mode:
            self._render_object

    def draw_ui(self) -> None:
        if self._debug_mode:
            debug_text: str = str(
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

        elif self._debug_cursor_idx:
            self._delete_object(self._debug_cursor_idx)
            self._debug_cursor_idx = None
