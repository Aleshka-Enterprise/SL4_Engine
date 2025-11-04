import random
from typing import Tuple
from game.core.storage import storage
from game.core.mixins.render_mixin import RenderMixin
from game.core.systems.render_system import RenderSystem

class Particle(RenderMixin):
    def __init__(self, velocity: Tuple[float, float], lifetime: float = 1.0, particle_destroy_listener=None, **kwargs):
        super().__init__(**kwargs)

        self.velocity = velocity
        self._lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = random.uniform(2, 6)
        self._is_active = True
        self.dt = 0.03
        self._ignore_render_check = True
        self.particle_destroy_listener = particle_destroy_listener
        
        if self.is_active:
            RenderSystem.register(self)
        
        storage.particles.append(self)
        
    @property
    def render_layer(self) -> str:
        return 'particles'
    
    @property
    def lifetime(self):
        return self._lifetime
    
    @lifetime.setter
    def lifetime(self, value):
        self._lifetime = value
        self.max_lifetime = value
        
    def destroy(self):
        self.is_active = False
        if self.particle_destroy_listener:
            self.particle_destroy_listener(self)
        return super().destroy()
        
    @property
    def is_active(self):
        return self._is_active
    
    @is_active.setter
    def is_active(self, value):
        self._is_active = value
        if (value):
            RenderSystem.register(self)

    def update_before_render(self):
        self.x += self.velocity[0] * self.dt
        self.y += self.velocity[1] * self.dt
        self.lifetime -= self.dt
        if self.lifetime < 0:
            self.destroy()
    
    def prepare_to_render(self, camera):
        screen_pos = camera.apply((self.x, self.y))
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        color = (*self.color[:3], min(max(alpha, 0), 255))
        radius = int(self.size * (self.lifetime / self.max_lifetime))
        return {
            'type': 'circle',
            'data': [color, *screen_pos, radius],
        }