import random

from game.core.components.audio.audio_mixin import AudioMixin
from game.core.components.gameplay.event.event_mixin import EventMixin
from game.core.components.system_manager import SystemManager
from game.models.text.counter.counter import Counter
from game.settings import DISPLAY, KEYS
from game.core.components.utils.timer.timer_mixin import TimerMixin
from game.models.entities.plane.plane import Plane
from game.models.envirements.ground.ground import Ground
from game.models.envirements.building.building import Building
from game.models.system_objects.background.background import BackgroundLayer
from game.utils.types import Event, EventState


class FlappyBird(TimerMixin, AudioMixin, EventMixin):
    def __init__(self):
        self.play_sound('soundtrack', loops=-1)

    def run(self) -> None:
        self.player = Plane(width=190, height=100, y=200, x=200, on_dead=self.on_plane_dead)
        self.player.jump()
        self.ground = Ground(width=2000, height=500, y=640, z_index=10, color=[0, 155, 0])
        self.counter = Counter(font_name="flappy-font.ttf", text="asdsad", x=700, y=40, width=100, height=100, color=(255, 255, 255), font_size=50)
        BackgroundLayer(x=0, y=0, height=DISPLAY.HEIGHT - 150, width=DISPLAY.WIDTH, z_index=1)
        self.add_pipes_timer = self.add_timer([self.generate_buildings], seconds=1.5, loop=True, use_on_start=True)

        self.event_listener = [
            Event(KEYS.MENU, EventState.KEY_DOWN, self.toggle_stop_game),
        ]

    def on_plane_dead(self, *args, **kwargs):
        Building.is_movement_enabled = False
        self.event_listener = [
            Event(KEYS.JUMP, EventState.KEY_DOWN, self.restart_scene),
        ]
        self.add_timer([
            lambda: BackgroundLayer(x=0, y=0, height=DISPLAY.HEIGHT + 100, width=DISPLAY.WIDTH, state='game_over', z_index=9999)
            ], seconds=1)
    
    def on_building_passed(self):
        self.counter.score += 1
        self.play_sound('point')

    def restart_scene(self):
        SystemManager.destroy_all()
        Building.is_movement_enabled = True
        self.run()
        
    def generate_buildings(self) -> None:
        if not self.player.is_alive:
            self.add_pipes_timer.delete_timer()
            return

        random_number = random.randint(0, 400)

        for i in range(2):
            building = Building(
                width = 100,
                height = 500 + random_number if i == 1 else 1000,
                x = 2200,
                y = -500 if i == 1 else random_number + 200,
                speed = 10,
                destroy_on_render_exit = True,
                player=self.player
            )

            if (i == 1):
                building.on_passed = self.on_building_passed