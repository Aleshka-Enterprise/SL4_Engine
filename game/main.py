from game.core.components.render import RenderSystem
from game.core.components.system_manager import SystemManager
from game.models.system_objects.camera import Camera
from game.scenes.flappy_bird import FlappyBird
from game.settings import DEBUG, DISPLAY, FPS
from game.core.storage import GAME_STATE, storage
import pygame
import cProfile


def run() -> None:
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    SystemManager.init()

    FlappyBird()

    clock = pygame.time.Clock()

    if not storage.camera:
        storage.camera = Camera(screen_width=DISPLAY.WIDTH, screen_height=DISPLAY.HEIGHT)

    while GAME_STATE.IS_RUNNING:
        SystemManager.update()
        clock.tick(FPS)

        if DEBUG:
            RenderSystem.set_surrent_fps(clock.get_fps())


if __name__ == '__main__':
    if DEBUG:
        profiler = cProfile.Profile()
        profiler.enable()
        run()
        profiler.disable()
        profiler.dump_stats('game/game_profile.prof')
    else:
        run()