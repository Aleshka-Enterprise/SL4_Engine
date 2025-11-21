from game.core.systems.base_system import BaseSystem
from game.core.mixins.jump_mixin import JumpMixin
from game.core.systems.collision_system import CollisionSystem


class GravitySystem(BaseSystem):

    @classmethod
    def apply_gravity(cls) -> None:
        '''Применение гравитации'''
        for obj in cls.objects:
            obj.vel_y += obj.gravity
            obj.y += obj.vel_y

            landing_platform = None
            min_penetration = float('inf')

            for collision_object in CollisionSystem.visible_collision_object_list:
                if obj != collision_object and obj.rect.colliderect(collision_object.rect):
                    if obj.y > collision_object.y:
                        obj.y = collision_object.y + obj.height
                        if obj.rect.bottom - 20 < collision_object.y:
                            landing_platform = collision_object
                        if hasattr(collision_object, 'vel_y'):
                            obj.vel_y = collision_object.vel_y
                        else:
                            obj.vel_y = 0
                        if isinstance(obj, JumpMixin):
                            obj._is_jumping = False
                    else:
                        penetration = obj.y - collision_object.y
                        if penetration < min_penetration:
                            min_penetration = penetration
                            landing_platform = collision_object
                    break

            if landing_platform:
                obj.y = landing_platform.rect.top - obj.height
                obj.on_the_ground = True
                obj.vel_y = 0
                if isinstance(obj, JumpMixin):
                    obj._is_jumping = False
            else:
                obj.on_the_ground = False

    @classmethod
    def update(cls):
        cls.apply_gravity()
