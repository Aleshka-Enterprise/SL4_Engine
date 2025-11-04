from uuid import uuid4
from pygame import Rect


class BaseMixin:
    def __init__(self, id = None, x: int = 0, y: int = 0, width: int = 0, height: int = 0, *args, **kwargs):
        self._id = id or uuid4()
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._rect = Rect(self.x, self.y, self.width, self.height)
        self.__rect_is_dirty = False

    @property
    def x(self):
        return self._x or 0

    @x.setter
    def x(self, value):
        self._x = value
        self.__rect_is_dirty = True
  
    @property
    def y(self):
        return self._y or 0

    @y.setter
    def y(self, value):
        self._y = value
        self.__rect_is_dirty = True
        
    @property
    def width(self):
        return self._width or 0
    
    @width.setter
    def width(self, value):
        self._width = value
        self.__rect_is_dirty = True
        
    @property
    def height(self):
        return self._height or 0
    
    @height.setter
    def height(self, value):
        self._height = value
        self.__rect_is_dirty = True

    @property
    def rect(self) -> Rect:
        if self.__rect_is_dirty:
            self._rect.x = self.x
            self._rect.y = self.y
            self._rect.width = self.width
            self._rect.height = self.height
            self.__rect_is_dirty = False
        return self._rect
    
    def destroy(self):
        pass