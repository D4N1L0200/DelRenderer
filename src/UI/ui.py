import pygame
from UI.parser import Parser
from UI.content import Block, Button
from typing import Callable
from pathlib import Path


class UI:
    def __init__(self, screen_size: tuple[int, int], path: str = "UI/") -> None:
        self.layout_path: Path = Path.cwd() / path / "layout"
        self.blocks: dict[str, Block] = {}
        self.screen_size: tuple[int, int] = screen_size
        self.bound_buttons: dict[str, Callable] = {}

        self.reload()

    def update_blocks(self, size: tuple[int, int]) -> None:
        self.screen_size = size

        for block in list(self.blocks.values()):
            block.update_pos(self.screen_size)

    def reload(self) -> None:
        self.blocks = Parser.parse(self.layout_path)
        self.update_blocks(self.screen_size)
        for path, callback in self.bound_buttons.items():
            self.bind_button(path, callback)

    def get_buttons(self) -> list[Button]:
        return [
            button
            for block in list(self.blocks.values())
            for button in block.get_buttons()
        ]

    def clear_clicks(self, mouse_button: int) -> None:
        for button in self.get_buttons():
            button.is_held[mouse_button] = False

    def press(self, pos: tuple[int, int], mouse_button: int) -> bool:
        for block in list(self.blocks.values()):
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

    def bind_button(self, button_path: str, callback: Callable) -> None:
        if button_path not in self.bound_buttons.keys():
            self.bound_buttons[button_path] = callback

        block_id, button_id = button_path.split("/")

        self.blocks[block_id].buttons[button_id].callback = callback

    def draw(self, window: pygame.Surface, font: pygame.font.Font) -> None:
        for block in list(self.blocks.values()):
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
                text = font.render(button.text, True, button.text_color)
                window.blit(
                    text,
                    (
                        button.pos[0] + (button.size[0] - text.get_width()) / 2,
                        button.pos[1] + (button.size[1] - text.get_height()) / 2,
                    ),
                )
