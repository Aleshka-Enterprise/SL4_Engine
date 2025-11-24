from game.core.components.phisics.collision import CollisionMixin
from game.objects.envirements.envirement import Envirement


class Ground(Envirement, CollisionMixin):
    '''Простой класс земли'''
    def __init__(self, transparent: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.transparent = transparent

    @property
    def top(self):
        return self.rect.top
