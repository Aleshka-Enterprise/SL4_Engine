from typing import Literal
from game.core.components.phisics.collision import CollisionMixin
from game.core.components.phisics.gravity import GravityMixin
from game.core.components.phisics.move import MoveMixin
from game.core.components.render.particle import ParticleMixin
from game.core.components.render import RenderMixin
from game.models.entities.entity import Entity


class Shoot(RenderMixin, GravityMixin, ParticleMixin, CollisionMixin, MoveMixin):
    def __init__(
        self,
        direction: Literal['left', 'right'],
        owner_weapon=None,
        initializer=None,
        damage: int = 0,
        speed: int = 30,
        z_index: int = 7,
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
        self.used_colision = True
        self.destroy_on_render_exit = True
        
        self.z_index = z_index

    @property
    def hit_entity(self):
        return self._hit_entity

    @hit_entity.setter
    def hit_entity(self, value):
        self._hit_entity = value

    def destroy(self) -> None:
        if self.owner_weapon and isinstance(self.owner_weapon.shoot_list, list) and self in self.owner_weapon.shoot_list:
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
        
    def on_touched(self, obj):
        if obj and obj != self.initializer:
            if isinstance(obj, Entity) and self.initializer != obj and self.initializer and self.initializer.fraction != obj.fraction:
                self.damage_entity(obj)

            self.destroy()
        
        return super().on_touched(obj)

    def update_before_render(self) -> None:
        self.move()
        
        return super().update_before_render()
        
