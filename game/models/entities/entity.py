from game.core.components.audio import AudioMixin
from game.core.components.phisics.collision import CollisionMixin
from game.core.components.phisics.collision.collision_types import CollisionResponseTypes
from game.core.components.phisics.gravity import GravityMixin
from game.core.components.gameplay.health import HealthMixin
from game.core.components.gameplay.interactive import InteractiveMixin
from game.core.components.render import AnimationMixin
from game.models.items.weapons.weapon import Weapon
from pygame import Rect


class Entity(AnimationMixin, HealthMixin, AudioMixin, CollisionMixin, GravityMixin, InteractiveMixin):
    '''Базовый класс сущностей'''
    def __init__(
        self,
        weapon: Weapon = None,
        fraction: str = None,
        **kwargs
    ):
        super().__init__(**kwargs)

        self._init_audio_mixin()

        self.is_enemy = False
        self.weapon = weapon
        self.fraction = fraction
        self.collision_response = CollisionResponseTypes.PUSH

        if self.weapon:
            self.weapon.entity = self
        
        self.z_index = 4

    def can_move(self, new_x: int, new_y: int) -> bool:
        '''Проверяет возможность движения с учётом столкновений'''
        entity_new_rect = Rect(new_x, new_y, self.width, self.height - 10)
        colision_object = self.check_collision(entity_new_rect, [self])

        if colision_object:
            x = colision_object.x + colision_object.width if self.direction == 'left' else colision_object.x - self.width
            colision_object = self.check_collision(Rect(x, self.y, self.width, self.height), [self])
            if not colision_object:
                self.x = x
            return False

        return not colision_object

    def on_died(self) -> None:
        '''Срабатывает при смерти сущности'''
        res = super().on_died()
        if self.weapon:
            self.weapon.destroy()
        self.destroy()

        return res

    def take_item(self) -> None:
        item = super().take_item(ignore=[self.weapon])
        if item:
            if item.item_type == 'weapon' and not item.entity:
                if self.weapon:
                    self.weapon.entity = None
                self.weapon = item
                self.weapon.entity = self

    def drop_weapon(self):
        if self.weapon:
            self.weapon.entity = None
            self.weapon = None
