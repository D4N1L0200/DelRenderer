import time
import pygame
import numpy


class SetupOptions:
    def __init__(self) -> None:
        self.size: tuple[int, int] = (800, 600)
        self.window_flags: int = pygame.DOUBLEBUF
        self.allowed_events: list[int] = [pygame.QUIT, pygame.KEYDOWN]
        self.title: str = "Renderer"

    def set_size(self, size: tuple[int, int]) -> None:
        for i in size:
            if i < 1:
                raise ValueError("Size cannot be less than 1")
        self.size = size

    def enable_fullscreen(self) -> None:
        self.window_flags |= pygame.FULLSCREEN

    def enable_resizable(self) -> None:
        self.window_flags |= pygame.RESIZABLE
        self.allowed_events.append(pygame.VIDEORESIZE)

    def set_title(self, title: str) -> None:
        self.title = title


class RendererBase:
    def __init__(self, options: SetupOptions) -> None:
        flags: int = options.window_flags
        self._window: pygame.Surface = pygame.display.set_mode(options.size, flags, 8)
        pygame.init()
        pygame.event.set_allowed(options.allowed_events)
        pygame.display.set_caption(options.title)
        info = pygame.display.Info()
        self._win_width, self._win_height = (
            info.current_w,
            info.current_h,
        )

        pygame.mouse.set_visible(False)
        self._last_mouse_pos: numpy.ndarray | None = None
        self._middle_clicked: bool = False
        self._shift_hold: bool = False

        self._clock: pygame.time.Clock = pygame.time.Clock()

        self._debug_mode: bool = False
        self._debug_cursor_idx: int | None = None
        self._current_rendered: int = 0

        self.fonts: dict[str, pygame.font.Font] = {
            "default": pygame.font.Font(None, 24),
            "debug": pygame.font.SysFont("monospace", 28),
        }

    def _resize(self, width: int, height: int) -> None:
        self._win_width = width
        self._win_height = height

    def _poll_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.VIDEORESIZE:
                self._resize(event.w, event.h)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.mouse.get_rel()
                elif event.key == pygame.K_F1:
                    self._toggle_debug()
                else:
                    self.key_pressed(
                        event.key, event.mod, event.unicode, event.scancode
                    )
            elif event.type == pygame.KEYUP:
                self.key_released(event.key, event.mod, event.unicode, event.scancode)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_pressed(event.pos, event.button)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_released(event.pos, event.button)

        return True

    def key_pressed(self, key: int, mod: int, unicode: str, scancode: int) -> None: ...
    def key_released(self, key: int, mod: int, unicode: str, scancode: int) -> None: ...
    def mouse_pressed(self, pos: tuple[int, int], button: int) -> None: ...
    def mouse_released(self, pos: tuple[int, int], button: int) -> None: ...
    def _toggle_debug(self) -> None: ...
    def update(self, dt: float) -> None: ...
    def create_object(self, obj_name: str, pos: tuple) -> None: ...
    def _delete_object(self, idx: int) -> None: ...
    def _render_objects(self) -> None: ...
    def draw_ui(self) -> None: ...

    def _draw_ui(self) -> None:
        pygame.draw.circle(
            self._window,
            (255, 255, 255),
            pygame.mouse.get_pos(),
            2,
        )

        self.draw_ui()

    def _draw(self) -> None:
        self._window.fill(0)

        self._render_objects()
        self._draw_ui()

        pygame.display.flip()

    def start(self) -> None:
        previous_time = time.time()
        running: bool = True
        while running:
            current_time = time.time()
            deltatime = current_time - previous_time

            running = self._poll_events()
            self.update(deltatime)
            self._draw()
            self._clock.tick(60)

            previous_time = current_time
            time.sleep(1 / 60)

        pygame.quit()
