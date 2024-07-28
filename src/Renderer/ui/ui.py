import pygame
from Renderer.ui.parser import Parser
from Renderer.ui.content import Block, Button




class UI:
    def __init__(self, screen_size: tuple[int, int]) -> None:
        self.path: str = "main.html"
        self.blocks: list[Block] = []
        self.screen_size: tuple[int, int] = screen_size
        
        self.reload()
        self.update_screen_size(self.screen_size)

    def update_screen_size(self, size: tuple[int, int]) -> None:
        self.screen_size = size
        
        for block in self.blocks:
            block.update_pos(self.screen_size)
        
    def reload(self) -> None:
        self.blocks = Parser.parse(self.path)

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
                text = font.render(button.text, True, button.text_color)
                window.blit(
                    text,
                    (
                        button.pos[0] + (button.size[0] - text.get_width()) / 2,
                        button.pos[1] + (button.size[1] - text.get_height()) / 2,
                    ),
                )
