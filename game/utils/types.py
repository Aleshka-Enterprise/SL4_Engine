from dataclasses import dataclass
from enum import Enum
from pyclbr import Function
from typing import Tuple


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
            self.on_change('extens', items)
    
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

class EventState(Enum):
    KEY_PRESSED = "key_pressed"    # Клавиша нажата
    KEY_DOWN = "key_down"          # Клавиша зажата
    KEY_UP = "key_up"              # Клавиша отпущена
    QUIT = "quit"                  # Закрытие окна

@dataclass
class Event:
    keys: Tuple[int]
    event_type: EventState
    callback: Function

    def __init__(self, keys: Tuple[int], event_type: EventState, callback: Function):
        self.keys = keys
        self.event_type = event_type
        self.callback = callback
