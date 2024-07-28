import pygame
from typing import Callable


class Button:
    def __init__(
        self,
        color: tuple[int, int, int],
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
            self.callback()
            self.is_held[pygame.BUTTON_LEFT] = False


class Block:
    def __init__(
        self,
        pos: tuple[int, int],
        direction: str,
        size: tuple[int, int],
        gap: int,
        padding: int,
        color: tuple[int, int, int],
        border_color: tuple[int, int, int],
        border_width: int,
        border_radius: int,
    ) -> None:
        self.pos: tuple[int, int] = pos
        self.direction: str = direction
        self.button_size: tuple[int, int] = size
        self.gap: int = gap
        self.padding: int = padding
        self.color: pygame.Color = pygame.Color(color)
        self.border_color: pygame.Color = pygame.Color(border_color)
        self.border_width: int = border_width
        self.border_radius: int = border_radius
        self.buttons: list[Button] = []

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
        button.pos = (self.pos[0] + self.padding, self.pos[1] + self.padding)
        button.size = self.button_size
        match self.direction:
            case "horizontal":
                button.pos = (
                    button.pos[0]
                    + (self.gap + self.button_size[0]) * len(self.buttons),
                    button.pos[1],
                )
            case "vertical":
                button.pos = (
                    button.pos[0],
                    button.pos[1]
                    + (self.gap + self.button_size[1]) * len(self.buttons),
                )
        self.buttons.append(button)

    def get_buttons(self) -> list[Button]:
        return self.buttons


class UI:
    def __init__(self) -> None:
        self.blocks: list[Block] = []

        block: Block = Block(
            (20, 20),
            "vertical",
            (50, 80),
            10,
            50,
            (255, 255, 255),
            (150, 150, 150),
            4,
            10,
        )
        block2: Block = Block(
            (220, 20),
            "horizontal",
            (80, 50),
            20,
            10,
            (255, 255, 255),
            (150, 150, 150),
            4,
            10,
        )

        block.add_button(
            Button(
                (255, 0, 255),
                (200, 0, 200),
                (0, 155, 0),
                5,
                5,
                "Test",
                lambda: print("test"),
            )
        )
        block.add_button(
            Button(
                (255, 0, 0),
                (200, 0, 0),
                (0, 0, 0),
                5,
                10,
                "Other",
                lambda: print("other"),
            )
        )

        block2.add_button(
            Button(
                (0, 255, 0),
                (0, 200, 0),
                (0, 0, 0),
                1,
                10,
                "Yeah",
                lambda: print("yeah"),
            )
        )
        block2.add_button(
            Button(
                (0, 0, 255),
                (0, 0, 200),
                (0, 0, 0),
                5,
                25,
                "Wow",
                lambda: print("wow"),
            )
        )

        self.blocks.append(block)
        self.blocks.append(block2)

    def get_buttons(self) -> list[Button]:
        return [button for block in self.blocks for button in block.get_buttons()]

    def clear_clicks(self, mouse_button: int) -> None:
        for button in self.get_buttons():
            button.is_held[mouse_button] = False

    def press(self, pos: tuple[int, int], mouse_button: int) -> bool:
        for block in self.blocks:
            if not block.is_inside(pos):
                continue

            for button in block.get_buttons():
                if not button.is_inside(pos):
                    continue

                button.start_click(mouse_button)
            return True

        return False

    def release(self, pos: tuple[int, int], mouse_button: int) -> bool:
        caught_click: bool = False

        for button in self.get_buttons():
            if not button.is_inside(pos):
                continue

            button.end_click(mouse_button)
            caught_click = True

        self.clear_clicks(mouse_button)
        return caught_click

    def draw(self, window: pygame.Surface, font: pygame.font.Font) -> None:
        for block in self.blocks:
            pygame.draw.rect(
                window,
                block.color,
                (*block.pos, *block.get_size()),
                0,
                block.border_radius,
            )
            pygame.draw.rect(
                window,
                block.border_color,
                (*block.pos, *block.get_size()),
                block.border_width,
                block.border_radius,
            )

            for button in block.get_buttons():
                color: pygame.Color = (
                    button.held_color if any(button.is_held.values()) else button.color
                )
                pygame.draw.rect(
                    window, color, (*button.pos, *button.size), 0, button.border_radius
                )
                pygame.draw.rect(
                    window,
                    button.border_color,
                    (*button.pos, *button.size),
                    button.border_width,
                    button.border_radius,
                )
                text = font.render(button.text, True, (0, 0, 0))
                window.blit(
                    text,
                    (
                        button.pos[0] + (button.size[0] - text.get_width()) / 2,
                        button.pos[1] + (button.size[1] - text.get_height()) / 2,
                    ),
                )
