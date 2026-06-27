from game.core.components.gameplay.event import EventMixin
from game.core.components.phisics.collision.collision_types import CollisionResponseTypes
from game.core.components.phisics.jump import JumpMixin
from game.models.entities.entity import Entity
from game.settings import KEYS
from game.utils.types import Event, EventState


class Plane(Entity, JumpMixin, EventMixin):
    def __init__(self, on_died = lambda: None, **kwargs):
        super().__init__(**kwargs)
        self._init_audio_mixin()

        self.jump_force = -8
        self.gravity = 0.3
        self._is_alive = True
        self.on_died = on_died
        self.collision_response = CollisionResponseTypes.IGNORE

        self.play_animation('jump', mode='freez')

        self.event_listener = [
            Event(KEYS.JUMP, EventState.KEY_DOWN, self.jump),
        ]
        
    @property
    def is_alive(self):
        return self._is_alive
    
    @is_alive.setter
    def is_alive(self, value):
        if not value and value != self._is_alive:
            self.play_sound('died')
            self.play_animation('destroed', mode='freez')
            self.on_died()
        self._is_alive = value

    def jump(self):
        return super().jump()
        
    def can_jump(self):
        return self.is_alive
    
    def on_start_jump(self):
        self.play_sound('flap')
        return super().on_start_jump()
    
    def can_move(self, new_x, new_y):
        return False
    
    def on_collision(self, obj) -> None:
        self.is_alive = False
        return super().on_collision(obj)
        
    def update_before_render(self):
        if self.is_alive and self.on_the_ground:
            self.is_alive = False
        return super().update_before_render()
