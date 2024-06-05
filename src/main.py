from Renderer import Renderer2D, SetupOptions
from Renderer import pygame as pg


class DelRend(Renderer2D):
    def __init__(self) -> None:
        options: SetupOptions = SetupOptions()
        options.set_size((800, 600))
        options.enable_resizable()
        options.set_title("DelRenderer")
        super().__init__(options)

    # TODO: Add keyboard functionality
    # def key_pressed(self, key: int, mod: int, unicode: str, scancode: int) -> None:
    #     if key == pg.K_w:
    #         pass
    #     elif key == pg.K_a:
    #         pass
    #     elif key == pg.K_s:
    #         pass
    #     elif key == pg.K_d:
    #         pass

    def mouse_pressed(self, pos: tuple[int, int], button: int) -> None:
        if button == pg.BUTTON_LEFT:
            self.create_object("square", self._camera.pos)
        elif button == pg.BUTTON_MIDDLE:
            pass
        elif button == pg.BUTTON_RIGHT:
            pass
        elif button == pg.BUTTON_WHEELUP:
            self.zoom(5)
        elif button == pg.BUTTON_WHEELDOWN:
            self.zoom(-5)

    # TODO: Add update functionality
    # def update(self, dt: float) -> None:
    #     super().update(dt)


if __name__ == "__main__":
    renderer: DelRend = DelRend()
    renderer.start()
