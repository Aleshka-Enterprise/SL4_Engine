import math
import random
from game.core.mixins.base_mixin import BaseMixin
from game.objects.particles.particle import Particle
from game.core.storage import storage


class ParticleMixin(BaseMixin):
    def __init__(self, max_particles = 300, **kwargs):
        super().__init__(**kwargs)

        self.max_particles = max_particles
    
    def __get_inactive_particles(self):
        return [particle for particle in storage.particles if not particle.is_active]
        
    def add_explosion_particles(self, x: float = None, y: float = None, color=(255, 100, 50), count=20):
        particle_x = x or self.x
        particle_y = y or self.y

        for _ in range(count):
            if len(storage.particles) > self.max_particles:
                break
            
            angle = random.uniform(0, 6.28)
            speed = random.uniform(50, 200)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed

            new_particle = Particle(
                x=particle_x,
                y=particle_y,
                width=10,
                height=10,
                color=color,
                velocity=(vx, vy),
                lifetime=random.uniform(0.5, 1.5),
            )

            count -= 1

        for particle in self.__get_inactive_particles()[0:count]:
            angle = random.uniform(0, 6.28)
            speed = random.uniform(50, 200)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed

            particle.x=particle_x
            particle.y=particle_y
            particle.width=10
            particle.height=10
            particle.color=color
            particle.velocity=[vx, vy]
            particle.lifetime=random.uniform(0.5, 2.0)
            particle.is_active = True

    def add_blood_particles(self, x: float, y: float, intensity=10):
        particle_x = x or self.x
        particle_y = y or self.y        
        
        for _ in range(intensity):
            if len(storage.particles) > self.max_particles:
                break

            new_particle = Particle(
                x=particle_x,
                y=particle_y, 
                width=10,
                height=10,
                color=(random.randint(120, 200), 0, 0),
                velocity=(random.uniform(-100, 100), random.uniform(-100, 0)),
                lifetime=random.uniform(1.0, 3.0),
            )

            intensity -= 1

        for particle in self.__get_inactive_particles()[0:intensity]:
            particle.x=particle_x
            particle.y=particle_y
            particle.width=10
            particle.height=10
            particle.color=(random.randint(120, 200), 0, 0)
            particle.velocity=(random.uniform(-100, 100), random.uniform(-100, 0))
            particle.lifetime=random.uniform(1.0, 3.0)
            particle.auto_register_in_render_system=False
            particle.is_active = True
