import numpy as np


class Object:
    def __init__(self) -> None:
        self.name: str = ""
        self.pos: np.array = np.array([0, 0, 0])
        self.vertices: list[np.array] = []
        self.edges: list[np.array] = []
        self.colors: dict[str, np.array] = {}
        self.items: list[dict] = []


class ObjectTemplate:
    def __init__(self, obj_params: dict) -> None:
        self.name: str = obj_params["name"]

        self.vertices: list[np.array] = [
            np.array(vertex) for vertex in obj_params["vertices"]
        ]
        self.edges: list[np.array] = [np.array(edge) for edge in obj_params["edges"]]

        self.colors: dict[str, np.array] = {}
        for color, rgb in obj_params["colors"].items():
            self.colors[color] = np.array(rgb)

        self.items: list[dict] = []
        for item in obj_params["render"]:
            self.items.append(item)

    def create_obj(self, pos: np.array) -> Object:
        obj = Object()
        obj.name = self.name
        obj.pos = pos
        obj.vertices = self.vertices
        obj.edges = self.edges
        obj.colors = self.colors
        obj.items = self.items
        return obj
