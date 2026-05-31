import random

from game.core.components.phisics.collision.collision_mixin import CollisionMixin
from game.core.components.phisics.move.move_mixin import MoveMixin
from game.models.envirements.envirement import Envirement


class Building(Envirement, MoveMixin, CollisionMixin):
    is_movement_enabled = True
 
    def __init__(self, transparent: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.transparent = transparent
        self.play_animation('default', mode='freez')

        if self._frames:
            self.current_frame_index = random.randint(0, len(self._frames) - 1)

    @property
    def top(self):
        return self.rect.top
    
    def update_before_render(self):
        if self.is_movement_enabled:
            self.move(self.direction)
        return super().update_before_render()