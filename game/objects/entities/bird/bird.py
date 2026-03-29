from game.core.components.gameplay.event import EventMixin
from game.core.components.phisics.jump import JumpMixin
from game.objects.entities.entity import Entity
from game.core.storage import storage
from game.settings import KEYS
from game.utils.types import Event, EventState


class Bird(Entity, JumpMixin, EventMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_audio_mixin()

        self._is_sitting = False
        self.default_height = kwargs.get('height', 100)
        self.jump_force = -11
        self.gravity = 0.3
        self.base_color = self.color
        self._is_alive = True

        self.event_listener = [
            Event(KEYS.JUMP, EventState.KEY_DOWN, self.jump),
        ]

        storage.player = self
        
    @property
    def is_alive(self):
        return self._is_alive
    
    @is_alive.setter
    def is_alive(self, value):
        if not value and value != self._is_alive:
            self.color = (200, 0, 0)
            self.play_sound('died')
        self._is_alive = value
        
    def can_jump(self):
        return self.is_alive
    
    def on_start_jump(self):
        self.play_sound('flap')
        return super().on_start_jump()
    
    def can_move(self, new_x, new_y):
        return False
    
    def update_before_render(self):
        if (self.check_collision(self.rect, ignore_list=[self.rect])) or self.on_the_ground:
            self.is_alive = False
        return super().update_before_render()
