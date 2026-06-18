from game.utils.types import ObservableList


class BaseSystem:
    objects = []
    is_freezable = True # Можно ли не обновлять систему в цикле (вызов меню и т.п.)

    @classmethod
    def on_change_objects_list(cls, action, item):
        ''' Слушатель изменений у списка objects '''
        pass

    @classmethod
    def register(cls, item):
        if not isinstance(cls.objects, ObservableList):
            cls.objects = ObservableList(cls.on_change_objects_list)
            
        if (isinstance(item, list)):
            cls.objects.extend(item)
        else:
            cls.objects.append(item)

    @classmethod
    def destroy(cls, item):
        cls.objects.remove(item)

    @classmethod
    def update(cls, dt: float = 1.0):
        pass

    @classmethod
    def destroy_all(cls):
        cls.objects.clear()
