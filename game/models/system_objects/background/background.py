import random

from game.core.components.render import AnimationMixin


class BackgroundLayer(AnimationMixin):
    def __init__(self, z_index=1, **kwargs):
        super().__init__(**kwargs)
        
        self.z_index = z_index
        self.play_animation("default", mode="random")

        if self._frames:
            self.current_frame_index = random.randint(0, len(self._frames) - 1)
