from pyclbr import Function
from typing import List


class Timer:
    def __init__(self, time: int, callbacks: List[Function], loop: bool = False, is_active: bool = True, **kwargs):
        super().__init__(**kwargs)

        self.time = time
        self.base_time = time
        self.callbacks = callbacks
        self.loop = loop
        self.__is_freezen = False
        self.__is_active = is_active
        
    @property
    def is_active(self):
        return self.__is_active
    
    @property
    def is_freezen(self):
        return self.__is_freezen
    
    def update(self) -> bool:
        ''' Обновление таймера. Возвращает bool - жив ли таймер '''
        if self.is_freezen:
            return True

        self.time -= 1

        if self.time <= 0:
            for callback in self.callbacks:
                callback()

            if self.loop:
                self.time = self.base_time
            else:
                return False

        return True
    
    def delete_timer(self):
        self.__is_active = False
        
    def freez_timer(self):
        self.__is_freezen = True
        
    def continue_timer(self):
        self.__is_freezen = False