from pyclbr import Function
from game.utils.systems_objects.timer import Timer
from typing import List, Tuple
from game.core.mixins.base_mixin import BaseMixin
from game.core.systems.timer_system import TimerSystem
from game.settings import FPS


class TimerMixin(BaseMixin):    
    def add_timer(
        self,
        callbacks: List[Function] | Tuple[Function],
        frames: int = 0,
        seconds: int = 0,
        minutes: int = 0,
        hours: int = 0,
        loop: bool = False,
        use_on_start: bool = False
    ) -> Timer:
        time = frames
        time += seconds * FPS
        time += minutes * 60 * FPS
        time += hours * 60 * 60 * FPS
        
        if use_on_start:
            for callback in callbacks:
                callback()

        new_timer = Timer(time, callbacks, loop)

        TimerSystem.register(new_timer)
        
        return new_timer
