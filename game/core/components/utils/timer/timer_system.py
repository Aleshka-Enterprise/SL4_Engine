from game.core.components.base.base_system import BaseSystem


class TimerSystem(BaseSystem):
    @classmethod
    def update(cls, dt: float = 1.0):
        for object in cls.objects:
            res = object.update(dt)
            if not res or not object.is_active:
                cls.objects.remove(object)
