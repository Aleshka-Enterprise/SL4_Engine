import random

from game.core.components.phisics.collision.collision_mixin import CollisionMixin
from game.core.components.phisics.move.move_mixin import MoveMixin
from game.models.envirements.envirement import Envirement


class Building(Envirement, MoveMixin, CollisionMixin):
    is_movement_enabled = True
 
    def __init__(self, transparent: bool = False, **kwargs):
        super().__init__(**kwargs)

        self.transparent = transparent
        self.is_passed = False

        self.play_animation('type_1', mode='freez')

        if self._frames:
            self.current_frame_index = random.randint(0, len(self._frames) - 1)
    
    def update_before_render(self, dt):
        if not self.is_passed and self.x < 200:
            self.is_passed = True
            self.on_passed()
        if self.is_movement_enabled:
            self.move(self.direction, dt)
        else:
            self.used_colision = False
        return super().update_before_render(dt)
    
    def on_passed(self):
        pass

    def play_destroy_building_animation(self):
        self.play_animation('type_1_destroed', mode='loop', timer=0.2)

    def on_touched(self, obj):
        if obj.__class__.__name__ != 'Ground':
            self.play_animation('type_1_destroed', mode='loop', timer=0.2)
        return super().on_touched(obj)