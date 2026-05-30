import random

from game.core.components.audio.audio_mixin import AudioMixin
from game.core.components.gameplay.event.event_mixin import EventMixin
from game.settings import DISPLAY, KEYS
from game.core.components.utils.timer.timer_mixin import TimerMixin
from game.models.entities.plane.plane import Plane
from game.models.envirements.ground.ground import Ground
from game.models.envirements.building.building import Building
from game.models.system_objects.background.background import BackgroundLayer
from game.utils.types import Event, EventState


class FlappyBird(TimerMixin, AudioMixin, EventMixin):
    def __init__(self):
        self.event_listener = [
            Event(KEYS.MENU, EventState.KEY_DOWN, self.toggle_stop_game),
        ]
        self.play_sound('soundtrack', loops=-1)

    def run(self) -> None:
        self.player = Plane(width=190, height=100, y=0, x=200)
        Ground(width=2000, height=500, y=640, z_index=100, color=[0, 155, 0])
        BackgroundLayer(x=0, y=0, height=DISPLAY.HEIGHT - 150, width=DISPLAY.WIDTH)
        self.add_pipes_timer = self.add_timer([self.generate_buildings], seconds=1.5, loop=True, use_on_start=True)
        
    def generate_buildings(self) -> None:
        if not self.player.is_alive:
            self.add_pipes_timer.delete_timer()
            return

        random_number = random.randint(0, 400)

        for i in range(2):
            Building(
                width = 100,
                height = 500 + random_number if i == 1 else 1000,
                x = 2200,
                y = -500 if i == 1 else random_number + 200,
                speed = 10,
                destroy_on_render_exit = True,
                player=self.player
            )