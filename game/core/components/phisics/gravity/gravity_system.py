from game.core.components.base.base_system import BaseSystem
from game.core.components.phisics.collision.collision_system import CollisionSystem


class GravitySystem(BaseSystem):

    @classmethod
    def apply_gravity(cls, dt: float) -> None:
        '''Применение гравитации с правильным dt'''
        for obj in cls.objects:
            obj.vel_y += obj.gravity * dt
            obj.y += obj.vel_y * dt
            
            landing_platform = None
            min_penetration = float('inf')
            
            collision_object = CollisionSystem.check_collision(obj.rect, [obj])

            if collision_object:
                if obj.y > collision_object.y:
                    if hasattr(collision_object, 'vel_y'):
                        obj.vel_y = collision_object.vel_y
                    else:
                        obj.vel_y = 0
                else:
                    penetration = obj.y - collision_object.y
                    if penetration < min_penetration:
                        min_penetration = penetration
                        landing_platform = collision_object

            if landing_platform:
                obj.y = landing_platform.rect.top - obj.height
                obj.on_the_ground = True
                obj.vel_y = 0
                obj.on_lend(landing_platform)
                landing_platform.on_landed(obj)
            else:
                obj.on_the_ground = False

    @classmethod
    def update(cls, dt: float = 1.0):
        cls.apply_gravity(dt)