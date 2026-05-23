from game.core.components.base.base_mixin import BaseMixin
from game.core.components.phisics.collision.collision_system import CollisionSystem
from game.core.components.phisics.collision.collision_types import CollisionResponseTypes


class CollisionMixin(BaseMixin):
    ''' Миксин отвечающий за добавление и обработку коллизии '''
    def __init__(
        self,
        used_colision: bool = True,
        collision_response: CollisionResponseTypes = CollisionResponseTypes.IGNORE,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.used_colision = used_colision
        self.collision_response = collision_response

    @property
    def used_colision(self):
        return self._used_colision

    @used_colision.setter
    def used_colision(self, value):
        if value and self not in CollisionSystem.objects:
            CollisionSystem.register(self)
        elif self in CollisionSystem.objects:
            CollisionSystem.destroy(self)

        self._used_colision = value

    def check_collision(self, rect, ignore_list=None):
        if ignore_list is None:
            ignore_list = []
        return CollisionSystem.check_collision(rect, ignore_list)

    def destroy(self):
        super().destroy()
        CollisionSystem.destroy(self)
        
    def on_collision(self, obj) -> None:
        pass
