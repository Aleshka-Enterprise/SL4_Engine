import random

from game.core.components.render import AnimationMixin


class BackgroundLayer(AnimationMixin):
    def __init__(self, z_index=1, state='default', mode: str = 'freeze', **kwargs):
        super().__init__(**kwargs)

        self.z_index = z_index
        self.play_animation(state, mode=mode)

        if self._frames:
            self.current_frame_index = random.randint(0, len(self._frames) - 1)
