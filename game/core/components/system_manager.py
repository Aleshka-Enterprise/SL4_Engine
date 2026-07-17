from game.core.components.gameplay.event import EventsSystem
from game.core.components.phisics.collision import CollisionSystem
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

    NON_FREEZING_SYSTEMS_LIST = [system for system in SYSTEMS_LIST if not system.is_freezable]

    @classmethod
    def init(cls) -> None:
        RenderSystem.init_window()

    @classmethod
    def update(cls, dt: float = 1.0) -> None:
        list = cls.NON_FREEZING_SYSTEMS_LIST if EventsSystem.is_frozen else cls.SYSTEMS_LIST
        for system in list:
            system.update(dt)

    @classmethod
    def destroy_all(cls) -> None:
        for system in cls.SYSTEMS_LIST:
            system.destroy_all()
