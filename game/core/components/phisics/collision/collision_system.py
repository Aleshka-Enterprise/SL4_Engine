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
    def check_collision(cls, rect, ignore_list=None):
        if ignore_list is None:
            ignore_list = []

        for collision_object in cls.visible_collision_object_list:
            if collision_object not in ignore_list and rect.colliderect(collision_object.rect):
                return collision_object
            
    @classmethod
    def update(cls):
        for obj in cls.visible_collision_object_list:
            collision_object = cls.check_collision(obj.rect, [obj])
            if collision_object:
                obj.on_collision(collision_object)
                if obj.collision_response == CollisionResponseTypes.PUSH and obj.y > collision_object.y:
                    if (collision_object.y + collision_object.height) // (obj.y + (obj.height // 2)) == 2:                            
                        obj.y = collision_object.y - obj.height
                    else:
                        obj.y = collision_object.y + collision_object.height
        return super().update()
