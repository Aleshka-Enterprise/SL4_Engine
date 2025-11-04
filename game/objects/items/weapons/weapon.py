from game.core.mixins.collision_mixin import CollisionMixin
from game.core.mixins.gravity_mixin import GravityMixin
from game.core.mixins.render_mixin import RenderMixin
from game.core.mixins.timer_mixin import TimerMixin
from game.core.storage import storage
from game.core.mixins.audio_mixin import AudioMixin
from game.objects.items.item import Item


class Weapon(Item, AudioMixin, RenderMixin, CollisionMixin, TimerMixin, GravityMixin):
    def __init__(self,
                 offset_x: int,
                 offset_y: int,
                 entity = None,
                 cooling_down: int = 30,
                 maximum_number_of_bullets: int = 10,
                 delete_after_death: bool = False,
                 gravity: float = 0.7,
                 damage: float = 1,
                 **kwargs
                 ):
        super().__init__(**kwargs)

        self._init_audio_mixin()
        
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.cooling_down = cooling_down
        self.maximum_number_of_bullets = maximum_number_of_bullets
        self.shoot_list = []
        self.entity = entity
        self.delete_after_death = delete_after_death
        self.vel_y = 0
        self.gravity = gravity
        self.weapon_is_ready = True
        self.damage = damage
        
        self.is_pickable = True
        
    @property
    def item_type(self):
        return 'weapon'
    
    @property
    def entity(self):
        return self._entity
    
    @entity.setter
    def entity(self, value):
        self.used_colision = not bool(value)
        self._entity = value
    
    def chenge_weapon_status(self, value):
        self.weapon_is_ready = value
        
    def can_atack(self) -> bool:
        if self.weapon_is_ready and len(self.shoot_list) < self.maximum_number_of_bullets:
            self.play_sound('shoot')
            self.add_timer(
                [lambda: self.chenge_weapon_status(True)],
                frames=self.cooling_down,
                loop=False
            )
            self.chenge_weapon_status(False)
            return True
            
        return False
    
    def attack(self) -> None:
        pass
        
    def update_before_render(self):
        if self.entity:
            direction = self.entity.direction
            self.y = self.entity.y + self.offset_y
            self.x = self.entity.x + self.offset_x
            if direction == 'right':
                self.x += self.entity.width
            
    def destroy(self) -> None:
        if self.entity:
            self.entity = None
        if self in storage.items and self.delete_after_death:
            storage.items.remove(self)
