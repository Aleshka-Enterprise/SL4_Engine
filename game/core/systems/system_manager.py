from game.core.systems.collision_system import CollisionSystem
from game.core.systems.events_system import EventsSystem
from game.core.systems.gravity_system import GravitySystem
from game.core.systems.render_system import RenderSystem
from game.core.systems.timer_system import TimerSystem


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