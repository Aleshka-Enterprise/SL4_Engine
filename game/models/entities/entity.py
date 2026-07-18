from game.core.components.audio import AudioMixin
from game.core.components.gameplay.health import HealthMixin
from game.core.components.phisics.collision import CollisionMixin
from game.core.components.phisics.collision.collision_types import CollisionResponseTypes
from game.core.components.phisics.gravity import GravityMixin
from game.core.components.render import AnimationMixin
from game.models.items.weapons.weapon import Weapon


class Entity(
    AnimationMixin,
    HealthMixin,
    AudioMixin,
    CollisionMixin,
    GravityMixin,
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
