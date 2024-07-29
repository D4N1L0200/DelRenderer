from Renderer import Renderer2D, Renderer3D, SetupOptions
from Renderer import pygame as pg
from random import random


class DelRend2D(Renderer2D):
    def __init__(self) -> None:
        options: SetupOptions = SetupOptions()
        options.set_size((800, 600))
        options.enable_resizable()
        options.set_title("DelRenderer 2D")
        super().__init__(options)

    def key_pressed(self, key: int, mod: int, unicode: str, scancode: int) -> None:
        if key == pg.K_F2:
            for _ in range(100):
                pos: tuple[float, float] = (
                    self._camera.pos[0] + random() * 20 - 10,
                    self._camera.pos[1] + random() * 20 - 10,
                )
                self.create_object("square", pos)


class DelRend3D(Renderer3D):
    def __init__(self) -> None:
        options: SetupOptions = SetupOptions()
        options.set_size((800, 600))
        options.enable_resizable()
        options.set_title("DelRenderer 3D")
        super().__init__(options)

    def spawn_random(self, amount: int = 100) -> None:
        for _ in range(amount):
            pos: tuple[float, float, float] = (
                self._camera.focus[0] + random() * 20 - 10,
                self._camera.focus[1] + random() * 20 - 10,
                self._camera.focus[2] + random() * 20 - 10,
            )
            self.create_object("cube", pos)

    def bind_buttons(self) -> None:
        self.ui.bind_button("main/debug", self._toggle_debug)
        self.ui.bind_button("main/random", self.spawn_random)
        self.ui.bind_button("main/reload", self.ui.reload)

    def key_pressed(self, key: int, mod: int, unicode: str, scancode: int) -> None:
        super().key_pressed(key, mod, unicode, scancode)

        if key == pg.K_F2:
            self.spawn_random()
        if key == pg.K_F5:
            self.ui.reload()


def main() -> None:
    renderer: DelRend3D = DelRend3D()
    renderer.start()


if __name__ == "__main__":
    main()
