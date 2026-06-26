import pygame

from game.core.components.base.base_system import BaseSystem
from game.core.components.phisics.collision.collision_types import CollisionResponseTypes
from game.core.storage import storage


class CollisionSystem(BaseSystem):
    visible_collision_object_list = []

    @classmethod
    def update_visible_objects(cls, visible_objects):
        '''Вызывается только при изменении зоны рендеринга'''
        cls.visible_collision_object_list = [elem for elem in cls.objects if elem in visible_objects and elem.used_colision]

    @classmethod
    def on_change_objects_list(cls, action, item):
        cls.update_visible_objects(storage.render_objects_list)
        return super().on_change_objects_list(action, item)

    @classmethod
    def check_collision(cls, rect: pygame.Rect, ignore_list=None):
        ''' Проверка столкновения '''
        if ignore_list is None:
            ignore_list = []

        for collision_object in cls.visible_collision_object_list:
            if collision_object.used_colision and collision_object not in ignore_list and rect.colliderect(collision_object.rect):
                return collision_object
            
    @classmethod
    def update(cls, dt: float = 1.0):
        for obj in cls.visible_collision_object_list:
            collision_object = cls.check_collision(obj.rect, [obj, *obj.collision_ignore_list])
            if collision_object:
                obj.on_collision(collision_object)
                if obj.collision_response == CollisionResponseTypes.PUSH and collision_object.collision_response != CollisionResponseTypes.IGNORE and not obj in collision_object.collision_ignore_list:
                    # Перекрытие по X
                    overlap_x = min(obj.rect.right - collision_object.rect.left,
                                    collision_object.rect.right - obj.rect.left)
                    # Перекрытие по Y
                    overlap_y = min(obj.rect.bottom - collision_object.rect.top,
                                    collision_object.rect.bottom - obj.rect.top)
                    if overlap_x < overlap_y:
                        # Выталкиваем по X
                        if obj.rect.centerx < collision_object.rect.centerx:
                            obj.x = collision_object.rect.left - obj.width
                        else:
                            obj.x = collision_object.rect.right
                    else:
                        # Выталкиваем по Y
                        if obj.rect.centery < collision_object.rect.centery:
                            obj.y = collision_object.rect.top - obj.height
                        else:
                            obj.y = collision_object.rect.bottom

        return super().update()
