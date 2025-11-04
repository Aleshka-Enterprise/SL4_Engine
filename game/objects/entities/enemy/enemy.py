from game.core.mixins.particle_mixin import ParticleMixin
from game.core.mixins.timer_mixin import TimerMixin
from game.objects.entities.entity import Entity
from game.core.storage import storage
import random


class Enemy(Entity, ParticleMixin, TimerMixin):
    def __init__(self, target: Entity = None, melee_damage: int = 10, patrol_distance = 200, viewing_radius=500, **kwargs):
        super().__init__(**kwargs)
        self.attack_timer = None
        self.is_enemy = True
        self.target = target or storage.player
        self.melee_damage = melee_damage
        self.target_is_detecte = False
        self.patrol_distance = patrol_distance
        self.patrol_points = [self.x - patrol_distance, self.x + patrol_distance]
        self.viewing_radius = viewing_radius
    
    @property
    def target_is_detecte(self):
        return self._target_is_detecte
    
    @target_is_detecte.setter
    def target_is_detecte(self, value):
        if value and self.weapon and self._target_is_detecte != value:
            self.attack_timer = self.add_timer(
                [self.weapon.attack],
                loop=True,
                frames=self.weapon.cooling_down,
                use_on_start=True
            )
        elif not value and self.attack_timer:
            self.attack_timer.delete_timer()
            
        self._target_is_detecte = value
            
    def on_died(self):
        if self.attack_timer:
            self.attack_timer.delete_timer()
        return super().on_died()
            
    def take_damage(self, damage):
        res = super().take_damage(damage)
        self.target_is_detecte = True
        return res
            
    def can_move(self, new_x, new_y):
        res = super().can_move(new_x, new_y)
        if not res and hasattr(self, 'is_jumping'):
            self.is_jumping = True
        return res
    
    def can_see_target(self):
        if self.target and ((self.x < self.target.x and self.direction == 'left') or (self.x > self.target.x and self.direction == 'right')):
            return False
        return not any(
            obstacle.rect.clipline(self.rect.center, self.target.rect.center)
            for obstacle in storage.grounds
        )
    
    def patrol(self):
        self.move(self.direction)
        if self.direction == 'left' and self.patrol_points[0] > self.x:
            self.direction = 'right'
        elif self.direction == 'right' and self.patrol_points[1] < self.x:
            self.direction = 'left'
            
        if self.target and abs(self.target.x - self.x) < self.viewing_radius and self.can_see_target():
            self.target_is_detecte = True
    
    def update_before_render(self):
        if not self.target_is_detecte or not self.target:
            self.patrol()
        if self.target_is_detecte:
            self.move('left' if self.x > self.target.x else 'right')
            if self.target.y < self.y and hasattr(self, 'is_jumping') and hasattr(self.target, 'is_jumping'):
                self.is_jumping = random.random() > 0.95

        return super().update_before_render()