from game.core.mixins.jump_mixin import JumpMixin
from game.objects.entities.enemy.enemy import Enemy


class Zombie(Enemy, JumpMixin):
    def on_died(self):
        res = super().on_died()
        self.play_sound('died')
        return res
    
    def on_move(self):
        res = super().on_move()
        self.play_sound('move')
        return res