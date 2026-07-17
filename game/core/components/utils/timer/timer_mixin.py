from pyclbr import Function
from typing import List, Tuple

from game.core.components.base.base_mixin import BaseMixin
from game.core.components.utils.timer.timer_system import TimerSystem
from game.utils.systems_objects.timer import Timer


class TimerMixin(BaseMixin):
    """Миксин отвечающий за добавлеине и работу с таймерами"""

    def add_timer(
        self,
        callback: Function,
        seconds: int = 0,
        loop: bool = False,
        call_immediately: bool = False,
    ) -> Timer:
        time = seconds

        if call_immediately:
            callback()

        new_timer = Timer(time, callback, loop)

        TimerSystem.register(new_timer)

        return new_timer
