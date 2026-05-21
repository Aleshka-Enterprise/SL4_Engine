import random

from game.core.components.utils.timer.timer_mixin import TimerMixin
from game.models.entities.bird.bird import Bird
from game.models.envirements.ground.ground import Ground
from game.models.envirements.ground.moving_platform.moving_platform import MovingPlatform


class FlappyBird(TimerMixin):
    @classmethod
    def run(cls):
        Bird(width=190, height=100, y=0, x=200, color=[255, 255, 0])
        Ground(width=2000, height=500, y=640, color=[0, 155, 0], z_index=100)
        
        cls.add_timer(cls, [cls.generate_platforms], seconds=1.5, loop=True, use_on_start=True)
        
    @classmethod
    def generate_platforms(cls):
        random_number = random.randint(000, 500)
        MovingPlatform(width=100, height=500 + random_number, x=2200, y=-500, speed=7, color=[0, 100, 30], destroy_on_render_exit=True)

        MovingPlatform(width=100, height=1000, x=2200, speed=7, color=[0, 100, 30], y=random_number+200, destroy_on_render_exit=True)
