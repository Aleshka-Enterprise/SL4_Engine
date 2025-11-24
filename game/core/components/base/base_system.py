from game.utils.types import ObservableList


class BaseSystem:
    objects = []

    @classmethod
    def on_change_objects_list(cls, action, item):
        ''' Слушатель изменений у списка objects '''
        pass

    @classmethod
    def register(cls, item):
        if not isinstance(cls.objects, ObservableList):
            cls.objects = ObservableList(cls.on_change_objects_list)
        cls.objects.append(item)

    @classmethod
    def destroy(cls, item):
        cls.objects.remove(item)

    @classmethod
    def register_list(cls, items):
        if not isinstance(cls.objects, ObservableList):
            cls.objects = ObservableList(cls.on_change_objects_list)
        cls.objects.extend(items)

    @classmethod
    def update(cls):
        pass
