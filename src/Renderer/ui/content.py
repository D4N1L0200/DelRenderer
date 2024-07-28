import pygame
from typing import Callable


class Button:
    def __init__(
        self,
        color: tuple[int, int, int],
        text_color: tuple[int, int, int],
        held_color: tuple[int, int, int],
        border_color: tuple[int, int, int],
        border_width: int,
        border_radius: int,
        text: str,
        callback: Callable,
    ) -> None:
        self.pos: tuple[int, int] = (0, 0)
        self.size: tuple[int, int] = (0, 0)
        self.color: pygame.Color = pygame.Color(color)
        self.text_color: pygame.Color = pygame.Color(text_color)
        self.held_color: pygame.Color = pygame.Color(held_color)
        self.border_color: pygame.Color = pygame.Color(border_color)
        self.border_width: int = border_width
        self.border_radius: int = border_radius
        self.text: str = text
        self.callback: Callable = callback
        self.is_held: dict[int, bool] = {
            pygame.BUTTON_LEFT: False,
            pygame.BUTTON_MIDDLE: False,
            pygame.BUTTON_RIGHT: False,
        }

    def is_inside(self, pos: tuple[int, int]) -> bool:
        return (
            self.pos[0] <= pos[0] <= self.pos[0] + self.size[0]
            and self.pos[1] <= pos[1] <= self.pos[1] + self.size[1]
        )

    def start_click(self, button: int) -> None:
        self.is_held[button] = True

    def end_click(self, button: int) -> None:
        if self.is_held[pygame.BUTTON_LEFT]:
            # self.callback() # TODO: FIX CALLBACK
            eval(self.callback)
            self.is_held[pygame.BUTTON_LEFT] = False


class Block:
    def __init__(
        self,
        rel_pos: tuple[int, int],
        size: tuple[int, int],
        direction: str,
        gap: int,
        padding: int,
        color: tuple[int, int, int],
        border_color: tuple[int, int, int],
        border_width: int,
        border_radius: int,
    ) -> None:
        self.rel_pos: tuple[int, int] = rel_pos
        self.pos: tuple[int, int] = rel_pos
        self.button_size: tuple[int, int] = size
        self.direction: str = direction
        self.gap: int = gap
        self.padding: int = padding
        self.color: pygame.Color = pygame.Color(color)
        self.border_color: pygame.Color = pygame.Color(border_color)
        self.border_width: int = border_width
        self.border_radius: int = border_radius
        self.buttons: list[Button] = []

    def update_pos(self, screen_size: tuple[int, int]) -> None:
        size: tuple[int, int] = self.get_size()
        self.pos = (
            (
                self.rel_pos[0] + screen_size[0] - size[0]
                if self.rel_pos[0] < 0
                else self.rel_pos[0]
            ),
            (
                self.rel_pos[1] + screen_size[1] - size[1]
                if self.rel_pos[1] < 0
                else self.rel_pos[1]
            ),
        )

        for idx, button in enumerate(self.buttons):
            self.buttons[idx] = self.update_button(button, idx)

    def update_button(self, button: Button, idx: int) -> Button:
        button.pos = (self.pos[0] + self.padding, self.pos[1] + self.padding)
        button.size = self.button_size
        match self.direction:
            case "horizontal":
                button.pos = (
                    button.pos[0]
                    + (self.gap + self.button_size[0]) * idx,
                    button.pos[1],
                )
            case "vertical":
                button.pos = (
                    button.pos[0],
                    button.pos[1]
                    + (self.gap + self.button_size[1]) * idx,
                )
        return button

    def get_size(self) -> tuple[int, int]:
        size = [
            self.button_size[0] + self.padding * 2,
            self.button_size[1] + self.padding * 2,
        ]

        match self.direction:
            case "horizontal":
                size[0] += (self.button_size[0] + self.gap) * (len(self.buttons) - 1)
            case "vertical":
                size[1] += (self.button_size[1] + self.gap) * (len(self.buttons) - 1)

        return size[0], size[1]

    def is_inside(self, pos: tuple[int, int]) -> bool:
        size = self.get_size()

        return (
            self.pos[0] <= pos[0] <= self.pos[0] + size[0]
            and self.pos[1] <= pos[1] <= self.pos[1] + size[1]
        )

    def add_button(self, button: Button) -> None:
        button = self.update_button(button, len(self.buttons))
        self.buttons.append(button)

    def get_buttons(self) -> list[Button]:
        return self.buttons
