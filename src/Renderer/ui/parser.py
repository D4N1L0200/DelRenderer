from Renderer.ui.content import Block, Button
from pathlib import Path
from typing import Any


class Parser:
    data_path: Path = Path.cwd() / "src" / "Renderer" / "data" / "ui"

    @staticmethod
    def merge_default(default: dict, override: dict) -> dict:
        merged: dict = default.copy()

        for key, value in override.items():
            merged[key] = value

        return merged

    @staticmethod
    def get_tag(html: str, tag: str) -> tuple[dict, str]:
        string = html.split("<" + tag, 1)[1]
        if "</" + tag + ">" in string:
            items = string.split("</" + tag + ">", 1)

            if ">" in items[0]:
                data, content = items[0].split(">", 1)

            if len(items) == 1:
                html = ""
            else:
                html = items[1]
        else:
            if "/>" in string:
                data, html = string.split("/>", 1)
                content = ""

        out: dict = {"content": content}

        while "=" in data:
            if data[0] != " ":
                raise ValueError("Invalid HTML")
            data = data[1:]

            key, data = data.split("=", 1)

            if data[0] != '"':
                raise ValueError("Invalid HTML")
            data = data[1:]

            value, data = data.split('"', 1)

            out[key] = value

        return out, html

    @staticmethod
    def get_tags(html: str, tag_name: str) -> list[dict]:
        tags: list[dict] = []
        while "<" + tag_name in html:
            tag, html = Parser.get_tag(html, tag_name)
            tags.append(tag)
        return tags

    @staticmethod
    def parse(path: str) -> list[Block]:
        with open(Parser.data_path / path, "r") as file:
            html: str = file.read()

        html = html.replace("\n", "")
        html = html.replace("\t", "")

        while "<!--" in html:
            start = html.find("<!--")
            end = html.find("-->")
            html = html[:start] + html[end + 3 :]

        main: dict = Parser.get_tag(html, "main")[0]

        header: dict = Parser.get_tag(main["content"], "header")[0]
        body: dict = Parser.get_tag(main["content"], "body")[0]

        link: dict = Parser.get_tag(header["content"], "link")[0]

        if link["rel"] != "stylesheet":
            raise ValueError("Invalid HTML")

        css: dict = Parser.parse_css(link["href"])

        block_tags: list[dict] = Parser.get_tags(body["content"], "block")

        blocks: dict[str, Block] = {}

        for block_tag in block_tags:
            block_id: str = "-1"
            try:
                block_id = block_tag["id"]
            except KeyError:
                pass

            button_tags: list[dict] = Parser.get_tags(block_tag["content"], "button")

            try:
                block_css: dict = css["block"][f"#{block_id}"]
            except KeyError:
                block_css = {}

            block_css = Parser.merge_default(css["*block"], block_css)

            pos: tuple[int, int] = block_css["position"]
            size: tuple[int, int] = block_css["size"]
            direction: str = block_css["direction"]
            anchor: str = block_css["offset-anchor"]
            gap: int = block_css["gap"]
            padding: int = block_css["padding"]
            background_color: tuple[int, int, int] = block_css["background-color"]
            border_color: tuple[int, int, int] = block_css["border-color"]
            border_width: int = block_css["border-width"]
            border_radius: int = block_css["border-radius"]

            block: Block = Block(
                pos,
                size,
                direction,
                anchor,
                gap,
                padding,
                background_color,
                border_color,
                border_width,
                border_radius,
            )

            for idx, button_tag in enumerate(button_tags):
                try:
                    button_css: dict = block_css["button"][f":nth({idx})"]
                except KeyError:
                    button_css = {}

                button_css = Parser.merge_default(css["*button"], button_css)

                background_color = button_css["background-color"]
                text_color = button_css["color"]
                held_color = button_css["accent-color"]
                border_color = button_css["border-color"]
                border_width = button_css["border-width"]
                border_radius = button_css["border-radius"]

                button = Button(
                    background_color,
                    text_color,
                    held_color,
                    border_color,
                    border_width,
                    border_radius,
                    button_tag["content"],
                    button_tag["onclick"],
                )

                block.add_button(button)

            blocks[block_id] = block

        return list(blocks.values())

    @staticmethod
    def parse_block(css_str: list[str], idx: int) -> tuple[dict, int]:
        block: dict = {}

        while ";" in css_str[idx]:
            key, line = css_str[idx][:-1].split(":", 1)

            block[key] = Parser.parse_css_value(line.strip())

            idx += 1

        while "}" not in css_str[idx]:
            if css_str[idx].startswith("button") and "{" in css_str[idx]:
                button_idx: str = css_str[idx].split(":nth(")[1].split(") {")[0].strip()

                idx += 1

                button: dict = {}

                while ";" in css_str[idx]:
                    key, line = css_str[idx][:-1].split(":", 1)

                    button[key] = Parser.parse_css_value(line.strip())

                    idx += 1

                if "button" not in block:
                    block["button"] = {}

                block["button"][f":nth({button_idx})"] = button

            idx += 1
        return block, idx

    @staticmethod
    def parse_css(path: str) -> dict:
        with open(Parser.data_path / path, "r") as file:
            css_str: list[str] = file.read().split("\n")

        css_str = [line.strip() for line in css_str if line != ""]

        css: dict = {"block": {}, "*block": {}, "*button": {}}

        idx: int = 0
        while idx < len(css_str):
            if css_str[idx].startswith("*block") and "{" in css_str[idx]:
                idx += 1

                css["*block"], idx = Parser.parse_block(css_str, idx)
            elif css_str[idx].startswith("*button") and "{" in css_str[idx]:
                idx += 1

                css["*button"], idx = Parser.parse_block(css_str, idx)
            elif css_str[idx].startswith("block") and "{" in css_str[idx]:
                block_id: str = css_str[idx].split("#")[1].split("{")[0].strip()

                idx += 1

                css["block"][f"#{block_id}"], idx = Parser.parse_block(css_str, idx)

            idx += 1

        return css

    @staticmethod
    def parse_css_value(value: str) -> Any:
        if value.startswith("rgb"):
            return tuple([int(x) for x in value[4:-1].split(",")])

        if "px" in value:
            out: tuple = tuple([int(x.replace("px", "")) for x in value.split()])

            if len(out) > 1:
                return out
            else:
                return out[0]

        return value
