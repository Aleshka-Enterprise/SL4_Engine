from game.core.mixins.audio_mixin import AudioMixin
from game.core.mixins.collision_mixin import CollisionMixin
from game.core.mixins.gravity_mixin import GravityMixin
from game.core.mixins.health_mixin import HealthMixin
from game.core.mixins.interactive_mixin import InteractiveMixin
from game.core.mixins.move_mixin import MoveMixin
from game.core.mixins.render_mixin import RenderMixin
from game.core.storage import storage
from game.objects.items.weapons.weapon import Weapon
from pygame import Rect


class Entity(RenderMixin, HealthMixin, AudioMixin, MoveMixin, CollisionMixin, GravityMixin, InteractiveMixin):
    '''Базовый класс сущностей'''
    def __init__(
        self,
        weapon: Weapon = None,
        show_hp: bool = False,
        **kwargs
    ):
        super().__init__(**kwargs)

        self._init_audio_mixin()

        self.is_enemy = False
        self.weapon = weapon
        self.show_hp = show_hp

        if self.weapon:
            self.weapon.entity = self

        storage.entities.append(self)
            
    @property
    def render_layer(self) -> str:
        return 'entity'
    
    def can_move(self, new_x: int, new_y: int, move_to_obstacle = True) -> bool:
        '''Проверяет возможность движения с учётом столкновений'''
        entity_new_rect = Rect(new_x, new_y, self.width, self.height)
        colision_object = self.check_collision(entity_new_rect, [self])

        if colision_object and self.rect.bottom - colision_object.rect.top < 10:
            entity_new_rect.y = colision_object.rect.top - self.height - 2

        colision_object = self.check_collision(entity_new_rect, [self])

        if not colision_object:
            self.y = entity_new_rect.y

        return not colision_object
    
    def on_died(self) -> None:
        '''Срабатывает при смерти сущности'''
        res = super().on_died()
        if self in storage.entities:
            storage.entities.remove(self)
            self.destroy()
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
