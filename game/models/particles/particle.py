from enum import Enum
import random
import math
from typing import Tuple
from game.core.components.render import RenderMixin
from game.core.components.render.render_types import RenderComand, RenderType


class ParticleFadeType(Enum):
    LINER = 'linear'
    EXPONENTIAL = 'exponential'
    QUADRATIC = 'quadratic'
    SQRT = 'sqrt'
    SINE = 'sine'


class Particle(RenderMixin):
    '''Группа частиц одного типа (взрыв, кровь и т.д.). Регистрируется как один объект в RenderSystem.'''
    _pool = []
    MAX_POOL_SIZE = 1000

    def __init__(
        self,
        x: float,
        y: float,
        count: int,
        particle_type: ParticleFadeType = ParticleFadeType.LINER,
        color: Tuple[int, int, int] = (255, 100, 50),
        lifetime_range: Tuple[float, float] = (0.5, 1.5),
        speed_range: Tuple[float, float] = (10, 30),
        size_range: Tuple[float, float] = (2, 6),
        gravity: Tuple[float, float] = (0, 0),
        spread_radius: float = 0.0,
        merge_threshold: float = 5.0,
        fade_type: str = 'linear',
        **kwargs
    ):
        kwargs.setdefault('z_index', 100)
        kwargs.setdefault('auto_register', True)
        kwargs.setdefault('_ignore_render_check', True)
        super().__init__(**kwargs)

        self.x = x
        self.y = y
        self.color = color
        self.particle_type = particle_type
        self.gravity = gravity
        self.spread_radius = spread_radius
        self.merge_threshold = merge_threshold
        self.fade_type = fade_type
        self._particles = []

        self._generate_particles(count, particle_type, color, lifetime_range, speed_range, size_range)

    def _generate_particles(self, count, particle_type, color, lifetime_range, speed_range, size_range):
        for _ in range(count):
            if particle_type == 'explosion':
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(*speed_range)
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed
                lifetime = random.uniform(*lifetime_range)
                size = random.uniform(*size_range)
                color = color
            elif particle_type == 'blood':
                vx = random.uniform(-100, 100)
                vy = random.uniform(-100, 0)
                lifetime = random.uniform(*lifetime_range)
                size = random.uniform(*size_range)
                color = (random.randint(120, 200), 0, 0)
            else:
                vx = random.uniform(-50, 50)
                vy = random.uniform(-50, 50)
                lifetime = random.uniform(*lifetime_range)
                size = random.uniform(*size_range)
                color = color

            # Координаты с разбросом
            px = self.x + random.uniform(-self.spread_radius, self.spread_radius)
            py = self.y + random.uniform(-self.spread_radius, self.spread_radius)

            # Проверка дубликатов
            merged = False
            if self.merge_threshold > 0:
                for existing in self._particles:
                    dx = existing['x'] - px
                    dy = existing['y'] - py
                    if dx*dx + dy*dy < self.merge_threshold * self.merge_threshold:
                        # Объединяем: увеличиваем размер и время жизни до максимума
                        existing['size'] = max(existing['size'], size)
                        existing['lifetime'] = max(existing['lifetime'], lifetime)
                        existing['max_lifetime'] = max(existing['max_lifetime'], lifetime)
                        # Можно смешать цвета (среднее арифметическое)
                        existing['color'] = (
                            (existing['color'][0] + color[0]) // 2,
                            (existing['color'][1] + color[1]) // 2,
                            (existing['color'][2] + color[2]) // 2
                        )
                        merged = True
                        break

            if not merged:
                particle = self._get_particle_data()
                particle['x'] = px
                particle['y'] = py
                particle['vx'] = vx
                particle['vy'] = vy
                particle['lifetime'] = lifetime
                particle['max_lifetime'] = lifetime
                particle['color'] = color
                particle['size'] = size
                particle['active'] = True
                self._particles.append(particle)

    def _get_particle_data(self):
        """Взять из пула или создать новый словарь."""
        if self._pool:
            return self._pool.pop()
        return {
            'x': 0, 'y': 0,
            'vx': 0, 'vy': 0,
            'lifetime': 0, 'max_lifetime': 0,
            'color': (0, 0, 0),
            'size': 0,
            'active': False
        }

    def _recycle_particle_data(self, data):
        if len(self._pool) < self.MAX_POOL_SIZE:
            data['active'] = False
            self._pool.append(data)

    def update_before_render(self, dt=0.03):
        for p in self._particles[:]:
            if not p['active']:
                continue
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['vx'] += self.gravity[0] * dt
            p['vy'] += self.gravity[1] * dt
            p['lifetime'] -= dt
            if p['lifetime'] <= 0:
                p['active'] = False
                self._particles.remove(p)
                self._recycle_particle_data(p)

        if not self._particles:
            self.destroy()

    def prepare_to_render(self, camera):
        commands = []
        for p in self._particles:
            if not p['active']:
                continue

            t = p['lifetime'] / p['max_lifetime']

            if self.fade_type == ParticleFadeType.LINER:
                factor = t
            elif self.fade_type == ParticleFadeType.EXPONENTIAL:
                factor = math.exp(-4 * (1 - t))
            elif self.fade_type == ParticleFadeType.QUADRATIC:
                factor = t * t
            elif self.fade_type == ParticleFadeType.SQRT:
                factor = math.sqrt(t)
            elif self.fade_type == ParticleFadeType.SINE:
                factor = math.sin(t * math.pi / 2)
            else:
                factor = t

            alpha = int(255 * factor)
            color = (*p['color'][:3], min(max(alpha, 0), 255))
            radius = int(p['size'] * factor)

            screen_pos = camera.apply((p['x'], p['y']))
            commands.append(RenderComand(
                type=RenderType.CIRCLE,
                data={'color': color, 'center': screen_pos, 'radius': radius}
            ))
        return commands