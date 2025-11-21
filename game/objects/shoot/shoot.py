from typing import Literal
from game.core.mixins.collision_mixin import CollisionMixin
from game.core.mixins.gravity_mixin import GravityMixin
from game.core.mixins.move_mixin import MoveMixin
from game.core.mixins.particle_mixin import ParticleMixin
from game.core.mixins.render_mixin import RenderMixin
from game.core.storage import storage
from game.objects.entities.entity import Entity


class Shoot(RenderMixin, GravityMixin, ParticleMixin, CollisionMixin, MoveMixin):
    def __init__(
        self,
        direction: Literal['left', 'right'],
        owner_weapon,
        initializer=None,
        damage: int = 0,
        speed: int = 30,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.direction = direction
        self.owner_weapon = owner_weapon
        self.damage = damage
        self.speed = speed
        self.initializer = initializer
        self._hit_entity = None
        self.gravity = 0.05
        self.vel_y = -0.1
        self.used_colision = False

        storage.shots.append(self)

    @property
    def render_layer(self) -> str:
        return 'shoot'

    @property
    def hit_entity(self):
        return self._hit_entity

    @hit_entity.setter
    def hit_entity(self, value):
        self._hit_entity = value

    def destroy(self) -> None:
        if (self in storage.shots):
            storage.shots.remove(self)
            self.destroy()
            self.owner_weapon.shoot_list.remove(self)

        return super().destroy()

    def render_particle(self, target: Literal['entity', 'ground']):
        '''Отрисовка частиц при столкновении'''
        if target == 'entity':
            self.add_blood_particles(self.x, self.y, intensity=13)

    def damage_entity(self, entity) -> None:
        entity.take_damage(self.damage)
        self.render_particle('entity')
        self.hit_entity = entity

    def on_exit_render_zone(self):
        self.destroy()
        return super().on_exit_render_zone()

    def update_before_render(self) -> None:
        super().move()

        colision_object = self.check_collision(self.rect, [])

        if colision_object:
            if isinstance(colision_object, Entity) and self.initializer != colision_object:
                self.damage_entity(colision_object)
            self.destroy()
            return
