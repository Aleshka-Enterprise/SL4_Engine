from game.core.systems.base_system import BaseSystem


class TimerSystem(BaseSystem):
    @classmethod
    def update(cls):
        for object in cls.objects:
            res = object.update()
            if not res or not object.is_active:
                cls.objects.remove(object)