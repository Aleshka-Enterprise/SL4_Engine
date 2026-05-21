from game.core.components.phisics.collision import CollisionMixin
from game.models.envirements.envirement import Envirement


class Ground(Envirement, CollisionMixin):
    '''Простой класс земли'''
    def __init__(self, transparent: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.transparent = transparent

    def static_animation(self) -> None:
        # self.play_animation('default', fps=10, mode='random')
        None

    @property
    def top(self):
        return self.rect.top
    
    def update_before_render(self):
        self.static_animation()
        return super().update_before_render()
