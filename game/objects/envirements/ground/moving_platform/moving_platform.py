from game.core.components.phisics.collision import CollisionMixin
from game.core.components.phisics.move.move_mixin import MoveMixin
from game.objects.envirements.envirement import Envirement
from game.objects.envirements.ground.ground import Ground


class MovingPlatform(Ground, MoveMixin):
    '''Простой класс земли'''
    def __init__(self, transparent: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.transparent = transparent

    @property
    def top(self):
        return self.rect.top
    
    def update_before_render(self):
        self.move(self.direction)
        return super().update_before_render()
