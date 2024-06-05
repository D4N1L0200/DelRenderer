from Renderer import Renderer2D, Renderer3D, SetupOptions
from Renderer import pygame as pg
from random import random


class DelRend2D(Renderer2D):
    def __init__(self) -> None:
        options: SetupOptions = SetupOptions()
        options.set_size((800, 600))
        options.enable_resizable()
        options.set_title("DelRenderer")
        super().__init__(options)

    def key_pressed(self, key: int, mod: int, unicode: str, scancode: int) -> None:
        if key == pg.K_F2:
            for _ in range(100):
                pos: tuple[float, float] = (
                    self._camera.pos[0] + random() * 20 - 10,
                    self._camera.pos[1] + random() * 20 - 10,
                )
                self.create_object("square", pos)


def main() -> None:
    renderer: DelRend2D = DelRend2D()
    renderer.start()


if __name__ == "__main__":
    main()
