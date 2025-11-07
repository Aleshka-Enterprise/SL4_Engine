from game.core.mixins.base_mixin import BaseMixin
from game.core.systems.collision_system import CollisionSystem


class CollisionMixin(BaseMixin):
    ''' Миксин отвечающий за добавление и обработку коллизии '''
    def __init__(self, used_colision = True, **kwargs):
        super().__init__(**kwargs)
        self.used_colision = used_colision
        
    @property
    def used_colision(self):
        return self._used_colision
    
    @used_colision.setter
    def used_colision(self, value):
        if value:
            CollisionSystem.register(self)
        else:
            CollisionSystem.destroy(self)
            
        self._used_colision = value
        
    def check_collision(self, rect, ignore):
        return CollisionSystem.check_collision(rect, ignore)
    
    def destroy(self):
        super().destroy()
        CollisionSystem.destroy(self)
