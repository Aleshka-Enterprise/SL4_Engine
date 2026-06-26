from game.utils.types import ObservableList


class BaseSystem:
    objects = []
    is_freezable = True

    @classmethod
    def on_change_objects_list(cls, action, item) -> None:
        ''' Слушатель изменений у списка objects '''
        pass

    @classmethod
    def register(cls, item) -> None:
        ''' Регистрация объекта в системе '''
        if not isinstance(cls.objects, ObservableList):
            cls.objects = ObservableList(cls.on_change_objects_list)
            
        if (isinstance(item, list)):
            cls.objects.extend(item)
        else:
            cls.objects.append(item)

    @classmethod
    def destroy(cls, item) -> None:
        ''' Удаление объекта из системы '''
        cls.objects.remove(item)

    @classmethod
    def update(cls, dt: float = 1.0) -> None:
        ''' Обновление на каждый тик '''
        pass

    @classmethod
    def destroy_all(cls) -> None:
        ''' Удаление всех объектов из системы '''
        cls.objects.clear()
