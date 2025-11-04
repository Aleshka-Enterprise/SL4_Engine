from game.core.mixins.render_mixin import RenderMixin
from game.core.storage import storage


class Envirement(RenderMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        storage.grounds.append(self)
        
    @property
    def render_layer(self) -> str:
        return 'envirement'