from typing import Literal, Tuple
from game.core.components.base.base_mixin import BaseMixin


class MoveMixin(BaseMixin):
    def __init__(
        self,
        speed: int = 0,
        direction: Literal['left', 'right'] = 'left',
        freez: bool = False,
        boost: int = 5,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.speed = speed
        self.direction = direction
        self.frez = freez
        self.boost = boost
        self._base_speed = speed
        self._is_running = False

    @property
    def base_speed(self):
        return self._base_speed

    @property
    def is_running(self):
        return self._is_running

    @is_running.setter
    def is_running(self, value):
        if self.can_run():
            if value and not self._is_running:
                self.speed = self.base_speed + self.boost
            elif not value and self._is_running:
                self.speed = self.base_speed
            self._is_running = value
        else:
            self._is_running = False

    def can_run(self) -> bool:
        return True

    def can_move(self, *args, **kwargs) -> bool:
        return True

    def on_move(self) -> None:
        pass

    def on_run(self) -> None:
        pass

    def move(self, new_direction: Literal['left', 'right'] = None) -> Tuple[int, int]:
        ''' Передвигает объект в сторону его движение и возвращает новые координаты '''
        direction = new_direction or self.direction
        x = self.x + self.speed * (-1 if direction == 'left' else 1)

        if self.direction != direction:
            self.direction = direction

        if self.can_move(x, self.y):
            if self.is_running:
                self.on_run()
            else:
                self.on_move()
            self.x = x

        return (self.x, self.y)

    def speed_boost(self):
        self.is_running = True

    def stop_speed_boost(self):
        self.is_running = False
