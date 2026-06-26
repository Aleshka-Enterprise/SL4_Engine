from enum import Enum

class CollisionResponseTypes(Enum):
    PUSH = "push"
    IGNORE = "ignore"
    STATIC = "static"