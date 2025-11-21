from typing import Literal
from game.core.mixins.event_mixin import EventMixin
from game.core.mixins.jump_mixin import JumpMixin
from game.objects.entities.entity import Entity
from game.core.storage import storage
from game.settings import KEYS
from game.core.storage import GAME_STATE
from game.utils.types import Event, EventState


class Player(Entity, JumpMixin, EventMixin):
    def __init__(self, energy: int = 350, **kwargs):
        super().__init__(**kwargs)

        self.energy = energy
        self.max_energy = energy
        self._is_sitting = False
        self.default_height = kwargs.get('height', 100)

        self.event_listener = [
            Event(KEYS.ATTACK, EventState.KEY_PRESSED, self.attack),
            Event(KEYS.LEFT, EventState.KEY_PRESSED, lambda: self.move('left')),
            Event(KEYS.RIGHT, EventState.KEY_PRESSED, lambda: self.move('right')),

            Event(KEYS.JUMP, EventState.KEY_DOWN, self.jump),
            Event(KEYS.RUN, EventState.KEY_DOWN, self.speed_boost),
            Event(KEYS.SIT, EventState.KEY_DOWN, self.sit),
            Event(KEYS.INTERACT, EventState.KEY_DOWN, self.take_item),
            Event(KEYS.DROP, EventState.KEY_DOWN, self.drop_weapon),

            Event(KEYS.RUN, EventState.KEY_UP, self.stop_speed_boost),
            Event(KEYS.SIT, EventState.KEY_UP, self.stand_up),
        ]

        storage.player = self

    @JumpMixin.is_jumping.setter
    def is_jumping(self, value):
        if self.energy < 100 and value and not self.is_sitting:
            self._is_jumping = False
        else:
            if value and not self._is_jumping:
                self.energy -= 100
            super(Player, Player).is_jumping.__set__(self, value)

    @Entity.is_running.setter
    def is_running(self, value):
        if not value or self.energy > 50 and not self.is_sitting:
            super(Player, Player).is_running.__set__(self, value)

    @property
    def is_sitting(self):
        return self._is_sitting

    @is_sitting.setter
    def is_sitting(self, value):
        if value and not self._is_sitting:
            self.height = self.height // 2
            self.speed = self.base_speed // 2
        elif not value and self._is_sitting:
            self.height = self.default_height
            self.speed = self.base_speed
        self._is_sitting = value

    def sit(self):
        self.is_sitting = True

    def stand_up(self):
        self.is_sitting = False

    def update_before_render(self):
        if self.energy < self.max_energy:
            self.energy = min(self.max_energy, self.energy + 1)
        super().update_before_render()

    def on_died(self):
        res = super().on_died()
        GAME_STATE.IS_RUNNING = False
        return res

    def on_take_damage(self):
        self.play_sound('damage')
        return super().on_take_damage()

    def on_move(self):
        res = super().on_move()
        if not self.is_jumping and not self.is_sitting and not self.is_running:
            self.play_sound('move')
        return res

    def on_run(self):
        self.energy -= 3

    def move(self, direction: Literal['left', 'right']):
        '''Движение Игрока'''
        res = super().move(direction)
        if self.energy < 10 or self.is_sitting:
            self.is_running = False
        return res

    def attack(self):
        if self.weapon:
            self.weapon.attack()
