from pyclbr import Function
from game.core.components.base.base_mixin import BaseMixin
from game.utils.systems_objects.timer import Timer
from typing import List, Tuple
from game.core.components.utils.timer.timer_system import TimerSystem


class TimerMixin(BaseMixin):
    ''' Миксин отвечающий за добавлеине и работу с таймерами '''
    def add_timer(
        self,
        callbacks: List[Function] | Tuple[Function],
        seconds: int = 0,
        loop: bool = False,
        use_on_start: bool = False
    ) -> Timer:
        time = seconds

        if use_on_start:
            for callback in callbacks:
                callback()

        new_timer = Timer(time, callbacks, loop)

        TimerSystem.register(new_timer)

        return new_timer
