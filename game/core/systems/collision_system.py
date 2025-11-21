from game.core.systems.base_system import BaseSystem
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
    def check_collision(cls, rect, ignore=[]):
        for collision_object in cls.objects:
            if collision_object not in ignore and rect.colliderect(collision_object.rect):
                return collision_object
