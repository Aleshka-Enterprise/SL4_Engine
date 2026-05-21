from game.core.components.render import AnimationMixin
from game.core.storage import storage


class Envirement(AnimationMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.z_index = kwargs.get('z_index', 2)

        storage.grounds.append(self)
