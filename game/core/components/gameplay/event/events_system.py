from typing import Tuple
import pygame
from game.core.components.base.base_system import BaseSystem
from game.core.storage import GAME_STATE
from game.utils.types import Event, EventState


class EventsSystem(BaseSystem):
    is_frozen = False
    _key_pressed_events: Tuple[Event] = []
    _key_down_events: Tuple[Event] = []
    _key_up_events: Tuple[Event] = []

    @classmethod
    def check_key(cls, keys: list[int]):
        pressed_keys = pygame.key.get_pressed()
        return any(pressed_keys[key] for key in keys)

    @classmethod
    def quit(cls):
        '''Выход из игры'''
        GAME_STATE.IS_RUNNING = False

    @classmethod
    def key_pressed_listener(cls):
        for event in cls._key_pressed_events:
            if cls.check_key(event.keys):
                event.callback()

    @classmethod
    def on_change_objects_list(cls, action, item):
        cls._key_pressed_events = [event for event in cls.objects if event.event_type == EventState.KEY_PRESSED]
        cls._key_down_events = [event for event in cls.objects if event.event_type == EventState.KEY_DOWN]
        cls._key_up_events = [event for event in cls.objects if event.event_type == EventState.KEY_UP]

    @classmethod
    def player_events(cls):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GAME_STATE.IS_RUNNING = False

    @classmethod
    def check_pressed_keys(cls, pressed_keys, keys):
        return any(pressed_keys[key] for key in keys)

    @classmethod
    def update(cls):
        pressed_keys = pygame.key.get_pressed()

        for event in cls._key_pressed_events:
            if cls.check_pressed_keys(pressed_keys, event.keys):
                event.callback()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                for keydown_event in cls._key_down_events:
                    if event.key in keydown_event.keys:
                        keydown_event.callback()
            elif event.type == pygame.KEYUP:
                for keyup_event in cls._key_up_events:
                    if event.key in keyup_event.keys:
                        keyup_event.callback()
            elif event.type == pygame.QUIT:
                cls.quit()

        return super().update()
