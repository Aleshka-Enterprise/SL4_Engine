import random

from game.core.components.utils.timer.timer_mixin import TimerMixin
from game.models.particles.particle import Particle


class ParticleMixin(TimerMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._particle_cooldown = {}

    def _can_call_particle(self, particle_type: str, cooldown_seconds: float) -> bool:
        if cooldown_seconds <= 0:
            return True
        key = f"particle_{particle_type}"
        if self._particle_cooldown.get(key, True):
            self._particle_cooldown[key] = False
            self.add_timer(
                lambda: self._particle_cooldown.__setitem__(key, True),
                seconds=cooldown_seconds,
                loop=False,
            )
            return True
        return False

    def add_explosion_particles(
        self,
        x=None,
        y=None,
        color="#FF6432",
        count=20,
        lifetime_range=(0.5, 1),
        speed_range=(-40, 40),
        size_range=(2, 4),
        spread_radius=0.0,
        merge_threshold=1.0,
        cooldown=1,
    ):
        if not self._can_call_particle("explosion", cooldown):
            return

        x = x or self.x + random.randint(-5, 5)
        y = y or self.y + random.randint(-5, 5)
        Particle(
            x=x,
            y=y,
            count=count,
            particle_type="explosion",
            color=color,
            lifetime_range=lifetime_range,
            speed_range=speed_range,
            size_range=size_range,
            spread_radius=spread_radius,
            merge_threshold=merge_threshold,
            ignore_render_check=True,
        )

    def add_blood_particles(
        self,
        x=None,
        y=None,
        intensity=10,
        fade_type="linear",
        lifetime_range=(1.0, 3.0),
        spread_radius=0.0,
        merge_threshold=5.0,
        cooldown=3,
    ):
        if not self._can_call_particle("blood", cooldown):
            return

        x = x or self.x
        y = y or self.y
        Particle(
            x=x,
            y=y,
            count=intensity,
            particle_type="blood",
            lifetime_range=lifetime_range,
            speed_range=(-100, 100),
            size_range=(2, 6),
            fade_type=fade_type,
            spread_radius=spread_radius,
            merge_threshold=merge_threshold,
            ignore_render_check=True,
        )
