from game.core.mixins.particle_mixin import ParticleMixin
from game.core.mixins.timer_mixin import TimerMixin
from game.objects.shoot.shoot import Shoot


class Poison(Shoot, ParticleMixin, TimerMixin):
    def __init__(self, experation_time, **kwargs):
        super().__init__(**kwargs)
        self._experation_time = experation_time
        self.entity_old_color = None
        self.poison_entity_timer = None

        self.particle_timer = self.add_timer([self.render_poison_particles], frames=2, loop=True)

    def render_poison_particles(self):
        self.add_explosion_particles(self.x, self.y, self.color, 5)

    def destroy(self):
        self.particle_timer.delete_timer()
        return super().destroy()

    @property
    def experation_time(self):
        return self._experation_time

    @Shoot.hit_entity.setter
    def hit_entity(self, value):
        if value:
            self.entity_old_color = value.color
            self._hit_entity = value
            value.color = (0, 70, 0)
            self.poison_entity_timer = self.add_timer(
                [
                    lambda: self.add_explosion_particles(value.x, value.y, self.color, 5),
                    lambda: self.hit_entity.take_damage(self.damage),
                    lambda: self.poison_entity_timer.delete_timer() if self.hit_entity and self.hit_entity.hp <= 0 else None
                ],
                frames=1,
                loop=True
            )
            self.add_timer(
                [
                    lambda: self.poison_entity_timer.delete_timer(),
                    lambda: self.destroy()
                ],
                frames=self.experation_time,
                loop=False
            )
            self.particle_timer.delete_timer()
        super(Poison, Poison).hit_entity.__set__(self, value)

    def update_before_render(self) -> None:
        if self.hit_entity and self.hit_entity.hp > 0:
            self.hit_entity.color = self.entity_old_color
            self.hit_entity = None
            self.destroy()

        return super().update_before_render()
