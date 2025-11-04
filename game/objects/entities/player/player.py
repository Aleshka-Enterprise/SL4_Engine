from typing import Literal
from game.core.mixins.jump_mixin import JumpMixin
from game.objects.entities.entity import Entity
from game.core.storage import storage


class Player(Entity, JumpMixin):
    def __init__(self, energy: int = 350, **kwargs):
        super().__init__(**kwargs)

        self.energy = energy
        self.max_energy = energy
        self._is_sitting = False
        self.base_height = kwargs.get('height', 100)
        
        storage.player = self

    @JumpMixin.is_jumping.setter
    def is_jumping(self, value):
        if self.energy < 100 and value and not self.is_sitting:
            self.is_jumping = False
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
            self.height = self.base_height
            self.speed = self.base_speed
        self._is_sitting = value
    
    def update_before_render(self):
        if self.energy < self.max_energy:
            self.energy = min(self.max_energy, self.energy + 1)
        super().update_before_render()
        
    def on_died(self):
        res = super().on_died()
        storage.game_options['running'] = False
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