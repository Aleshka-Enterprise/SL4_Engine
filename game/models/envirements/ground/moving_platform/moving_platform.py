import random

from game.core.components.phisics.move.move_mixin import MoveMixin
from game.models.envirements.ground.ground import Ground


class MovingPlatform(Ground, MoveMixin):
    '''Простой класс земли'''
    def __init__(self, transparent: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.transparent = transparent
        self.play_animation('default', mode='random', fps=5)

        if self._frames:
            self.current_frame_index = random.randint(0, len(self._frames) - 1)

    @property
    def top(self):
        return self.rect.top
    
    def update_before_render(self):
        self.move(self.direction)
        return super().update_before_render()
