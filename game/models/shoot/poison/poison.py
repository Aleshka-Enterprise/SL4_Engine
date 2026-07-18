from typing import Optional

from game.core.components.render.particle import ParticleMixin
from game.core.components.utils.timer import TimerMixin
from game.models.shoot.shoot import Shoot


class Poison(Shoot, ParticleMixin, TimerMixin):
    def __init__(self, experation_time, **kwargs):
        super().__init__(**kwargs)
        self._experation_time: Optional[int] = experation_time
        self.entity_old_color: Optional[str] = None
        self.poison_entity_timer: Optional[int] = None

        self.particle_timer = self.add_timer(self.render_poison_particles, seconds=0, loop=True)

    def render_poison_particles(self):
        self.add_explosion_particles(self.x, self.y, self.color, 5)

    def destroy(self):
        self.particle_timer.delete_timer()
        return super().destroy()

    @property
    def experation_time(self):
        return self._experation_time

    def _on_bullet_hit(self, value):
        """Вызывается при попадании пули"""
        self.add_explosion_particles(value.x, value.y, self.color, 5)
        self.hit_entity.take_damage(self.damage)

        if self.hit_entity and self.hit_entity.hp <= 0 and hasattr(self, "poison_entity_timer"):
            self.poison_entity_timer.delete_timer()

    @Shoot.hit_entity.setter
    def hit_entity(self, value):
        if value:
            self.entity_old_color = value.color
            self._hit_entity = value
            value.color = "#004600"
            self.poison_entity_timer = self.add_timer(
                lambda: self._on_bullet_hit(value),
                seconds=0,
                loop=True,
            )
            self.add_timer(
                [lambda: self.poison_entity_timer.delete_timer(), lambda: self.destroy()],
                seconds=self.experation_time,
                loop=False,
            )
            self.particle_timer.delete_timer()
        super(Poison, Poison).hit_entity.__set__(self, value)

    def update_before_render(self, dt) -> None:
        if self.hit_entity and self.hit_entity.hp > 0:
            self.hit_entity.color = self.entity_old_color
            self.hit_entity = None
            self.destroy()

        return super().update_before_render(dt)
