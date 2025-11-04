from game.utils.types import ObservableList


class BaseSystem:
    objects = []
    
    @classmethod
    def on_change(cls, action, item):
        pass

    @classmethod
    def register(cls, item):
        if not isinstance(cls.objects, ObservableList):
            cls.objects = ObservableList(cls.on_change)
        cls.objects.append(item)
        
    @classmethod
    def destroy(cls, item):
        cls.objects.remove(item)
        
    @classmethod
    def register_list(cls, items):
        cls.objects.extend(items)
        
    @classmethod
    def update(cls):
        pass