from game.core.systems.render_system import RenderSystem
from game.core.systems.system_manager import SystemManager
from game.objects.system_objects.camera import Camera
from game.settings import DEBUG, DISPLAY, FPS
from game.core.storage import storage
from game.system.saveload import save_level, load_level
import pygame
import cProfile

def run() -> None:
    load_level('game/levels/mario.json')

    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    SystemManager.init()

    clock = pygame.time.Clock()

    if not storage.camera:
        storage.camera = Camera(screen_width=DISPLAY.WIDTH, screen_height=DISPLAY.HEIGHT)
    
    while storage.game_options['running']:
        SystemManager.update()
        clock.tick(FPS)
        
        if DEBUG:
            RenderSystem.set_surrent_fps(clock.get_fps())
        
    if storage.player:
        save_level('game/levels/save.json')
    
if __name__ == '__main__':
    if DEBUG:
        cProfile.run('run()', 'game/game_profile.prof')
        profiler = cProfile.Profile()
        profiler.enable()

    run()

    if DEBUG:
        profiler.disable()
        profiler.dump_stats('game/game_profile.prof')