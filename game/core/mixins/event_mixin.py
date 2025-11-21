from typing import List
from game.core.mixins.base_mixin import BaseMixin
from game.core.systems.events_system import EventsSystem
from game.utils.types import Event


class EventMixin(BaseMixin):
    ''' Миксин отвечающий за обработку событий, по типу нажатия клавиш, событие мышки и т.п. '''
    def __init__(self, event_listener: List[Event] = [], **kwargs):
        self.__event_listener = event_listener
        super().__init__(**kwargs)

    @property
    def event_listener(self):
        return self.__event_listener

    @event_listener.setter
    def event_listener(self, value):
        self.__event_listener = value
        EventsSystem.register_list(self.__event_listener)
