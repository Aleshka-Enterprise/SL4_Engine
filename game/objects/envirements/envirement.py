from game.core.components.render import RenderMixin
from game.core.storage import storage


class Envirement(RenderMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.z_index = 2

        storage.grounds.append(self)
