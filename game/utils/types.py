from pygame import sprite, Surface


class RectSprite(sprite.Sprite):
    def __init__(self, x, y, width, height, color):
        super().__init__()
        self.image = Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

class ObservableList:
    def __init__(self, on_change=None):
        self._items = []
        self.on_change = on_change
    
    def append(self, item):
        self._items.append(item)
        if self.on_change:
            self.on_change('append', item)
    
    def remove(self, item):
        if item in self._items:
            self._items.remove(item)
            if self.on_change:
                self.on_change('remove', item)
    
    def extend(self, items):
        self._items.extend(items)
        if self.on_change:
            # TODO Перевести на разные callback функции внутри самих систем, которые используют этот тип. Убрать костыль.
            self.on_change('append', items[0])
    
    def clear(self):
        self._items.clear()
        if self.on_change:
            self.on_change('clear', None)
    
    def __len__(self):
        return len(self._items)
    
    def __getitem__(self, index):
        return self._items[index]
    
    def __iter__(self):
        return iter(self._items)
    
    def __repr__(self):
        return repr(self._items)


class LazyType:
    def __init__(self, module_path, class_name):
        self.module_path = module_path
        self.class_name = class_name
        self._resolved = None
    
    def __call__(self, *args, **kwargs):
        if self._resolved is None:
            module = __import__(self.module_path, fromlist=[self.class_name])
            self._resolved = getattr(module, self.class_name)
        return self._resolved(*args, **kwargs)
    
    def __instancecheck__(self, instance):
        if self._resolved is None:
            module = __import__(self.module_path, fromlist=[self.class_name])
            self._resolved = getattr(module, self.class_name)
        return isinstance(instance, self._resolved)