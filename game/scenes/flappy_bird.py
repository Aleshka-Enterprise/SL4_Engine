import random

from game.core.components.audio.audio_mixin import AudioMixin
from game.settings import DISPLAY
from game.core.components.utils.timer.timer_mixin import TimerMixin
from game.models.entities.bird.bird import Bird
from game.models.envirements.ground.ground import Ground
from game.models.envirements.ground.moving_platform.moving_platform import MovingPlatform
from game.models.system_objects.background.background import BackgroundLayer


class FlappyBird(TimerMixin, AudioMixin):
    def __init__(self):
        pass

    def run(self):
        self.player = Bird(width=190, height=100, y=0, x=200, color=[255, 255, 0])
        Ground(width=2000, height=500, y=640, color=[0, 155, 0], z_index=100)
        BackgroundLayer(x=0, y=0, height=DISPLAY.HEIGHT - 150, width=DISPLAY.WIDTH)
        
        self.add_pipes_timer = self.add_timer([self.generate_platforms], seconds=1.5, loop=True, use_on_start=True)
        self.play_sound('soundtrack', loops=-1)
        
    def generate_platforms(self):
        random_number = random.randint(0, 400)

        for i in range(2):
            MovingPlatform(
                width = 100,
                height = 500 + random_number if i == 1 else 1000,
                x = 2200,
                y = -500 if i == 1 else random_number + 200,
                speed = 10,
                destroy_on_render_exit = True,
                player=self.player
            )

        if not self.player.is_alive:
            self.add_pipes_timer.delete_timer()
