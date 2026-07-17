from game.core.components.phisics.collision import CollisionMixin
from game.models.envirements.envirement import Envirement


class Ground(Envirement, CollisionMixin):
    """Простой класс земли"""

    def __init__(self, transparent: bool = False, z_index=1, **kwargs):
        super().__init__(**kwargs)
        self.transparent = transparent
        self.z_index = z_index

    @property
    def top(self):
        return self.rect.top

    def update_before_render(self, dt):
        return super().update_before_render(dt)
