from game.core.components.base.base_mixin import BaseMixin
from game.core.components.phisics.collision.collision_system import CollisionSystem
from game.core.components.phisics.collision.collision_types import CollisionResponseTypes


class CollisionMixin(BaseMixin):
    """Миксин отвечающий за добавление и обработку коллизии"""

    def __init__(
        self,
        used_colision: bool = True,
        collision_response: CollisionResponseTypes = CollisionResponseTypes.STATIC,
        collision_ignore_list: list["CollisionMixin"] | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.used_colision = used_colision
        self.collision_response = collision_response
        self.collision_ignore_list = collision_ignore_list or []

        CollisionSystem.register(self)

    @property
    def used_colision(self):
        return self._used_colision

    @used_colision.setter
    def used_colision(self, value: bool):
        self._used_colision = value

    def check_collision(self, rect, ignore_list=None) -> "CollisionMixin" | None:
        """Проверка столкновения"""
        if ignore_list is None:
            ignore_list = []
        return CollisionSystem.check_collision(rect, ignore_list)

    def destroy(self) -> None:
        super().destroy()
        CollisionSystem.destroy(self)

    def on_collision(self, obj: "CollisionMixin") -> None:
        """Обработчик события: объект столкнулся"""
        self.on_touched(obj)

    def on_landed(self, obj: "CollisionMixin") -> None:
        """Обработчик события: объект приземлился"""
        self.on_touched(obj)

    def on_touched(self, obj: "CollisionMixin") -> None:
        """Обработчик события: объект был тронут"""
        pass
