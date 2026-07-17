from game.core.components.audio import AudioMixin
from game.core.components.gameplay.health import HealthMixin
from game.core.components.gameplay.interactive import InteractiveMixin
from game.core.components.phisics.collision import CollisionMixin
from game.core.components.phisics.collision.collision_types import CollisionResponseTypes
from game.core.components.phisics.gravity import GravityMixin
from game.core.components.phisics.move.move_mixin import MoveMixin
from game.core.components.render import AnimationMixin
from game.models.items.weapons.weapon import Weapon
from pygame import Rect


class Entity(
    AnimationMixin,
    MoveMixin,
    HealthMixin,
    AudioMixin,
    CollisionMixin,
    GravityMixin,
    InteractiveMixin,
):
    """Базовый класс сущностей"""

    def __init__(self, weapon: Weapon = None, fraction: str = None, z_index: int = 4, **kwargs):
        super().__init__(**kwargs)

        self._init_audio_mixin()

        self.is_enemy = False
        self.weapon = weapon
        self.fraction = fraction
        self.collision_response = CollisionResponseTypes.PUSH

        if self.weapon:
            self.weapon.entity = self

        self.z_index = z_index

    def can_move(self, new_x: int, new_y: int) -> bool:
        """Проверяет возможность движения (без коллизий)"""
        entity_new_rect = Rect(new_x, new_y, self.width, self.height)
        return self.check_collision(entity_new_rect, [self]) is None

    def on_died(self) -> None:
        """Срабатывает при смерти сущности"""
        res = super().on_died()
        if self.weapon:
            self.weapon.destroy()
        self.destroy()

        return res

    def take_item(self, dt=None) -> None:
        item = super().take_item(ignore=[self.weapon])
        if item and item.item_type == "weapon" and not item.entity:
            if self.weapon:
                self.weapon.entity = None
            self.weapon = item
            self.weapon.entity = self

    def drop_weapon(self, dt=None):
        if self.weapon:
            self.weapon.entity = None
            self.weapon = None

    # TODO объект сейчас не подходит к колизии вплотную
    def resolve_collision(self, new_x: int, new_y: int) -> tuple[int, int]:
        test_rect_x = Rect(new_x, self.y, self.width, self.height)
        if self.check_collision(test_rect_x, [self]) is None:
            test_rect_y = Rect(self.x, new_y, self.width, self.height)
            if self.check_collision(test_rect_y, [self]) is None:
                return (new_x, new_y)
            else:
                return (new_x, self.y)
        else:
            test_rect_y = Rect(self.x, new_y, self.width, self.height)
            if self.check_collision(test_rect_y, [self]) is None:
                return (self.x, new_y)
            else:
                return (self.x, self.y)
