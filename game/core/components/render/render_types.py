from enum import Enum


class RenderType(Enum):
    RECT = "rect"
    CIRCLE = "circle"
    TEXT = "text"
    IMAGE = "image"


class RenderComand:
    __slot__ = ("type", "data", "z_index")

    def __init__(self, type: RenderType = RenderType.RECT, data: dict = None, z_index: int = 0):
        self.type = type
        self.data = data
        self.z_index = z_index
