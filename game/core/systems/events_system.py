import pygame
from game.core.storage import storage
from game.core.systems.base_system import BaseSystem
from game.settings import KEYS


class EventsSystem(BaseSystem):
    is_freezen = False
    
    @classmethod
    def check_key(cls, keys: list[int]):
        pressed_keys = pygame.key.get_pressed()
        return any(pressed_keys[key] for key in keys)
    
    @classmethod
    def check_freez(cls):
        if cls.check_key(KEYS.MENU):
            cls.is_freezen = True
    
    @classmethod
    def quit():
        '''Выход из игры'''
        storage.game_options['running'] = False
    
    @classmethod
    def player_events(cls):
        if cls.check_key(KEYS.RIGHT):
            storage.player.move('right')
        elif cls.check_key(KEYS.LEFT):
            storage.player.move('left')
        if cls.check_key(KEYS.ATTACK) and storage.player.weapon:
            storage.player.weapon.attack()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cls.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key in KEYS.JUMP:
                    storage.player.is_jumping = True
                elif event.key in KEYS.RUN:
                    storage.player.is_running = True
                elif event.key in KEYS.SIT:
                    storage.player.is_sitting = True
                elif event.key in KEYS.INTERACT:
                    storage.player.take_item()
                elif event.key in KEYS.DROP:
                    storage.player.drop_weapon()

            elif event.type == pygame.KEYUP:
                if event.key in KEYS.RUN:
                    storage.player.is_running = False
                elif event.key in KEYS.SIT:
                    storage.player.is_sitting = False
                    
    @classmethod
    def update(cls):
        cls.player_events()
        return super().update()