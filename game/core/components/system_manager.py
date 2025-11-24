from game.core.components.phisics.collision import CollisionSystem
from game.core.components.gameplay.event import EventsSystem
from game.core.components.phisics.gravity import GravitySystem
from game.core.components.render import RenderSystem
from game.core.components.utils.timer import TimerSystem


class SystemManager:
    SYSTEMS_LIST = (
        EventsSystem,
        GravitySystem,
        CollisionSystem,
        TimerSystem,
        RenderSystem,
    )

    @classmethod
    def init(cls):
        RenderSystem.init_window()

    @classmethod
    def update(cls):
        if not EventsSystem.is_frozen:
            for system in cls.SYSTEMS_LIST:
                system.update()
