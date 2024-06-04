from renderer import Renderer


if __name__ == "__main__":
    # renderer: Renderer = Renderer(size=(800, 600), mode="2D")
    renderer: Renderer = Renderer(size=(800, 600), mode="3DWireframe")
    renderer.start()
