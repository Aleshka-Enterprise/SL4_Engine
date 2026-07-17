import math
from enum import Enum
from typing import Literal, Optional, Tuple, Union

from game.core.components.base.base_mixin import BaseMixin
from game.settings import DEBUG

Direction = Literal["left", "right", "up", "down", "up-left", "up-right", "down-left", "down-right"]


class MoveModeType(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    FREE = "free"
    COMPASS = "compass"


class CompassDirection(Enum):
    N = "n"
    NE = "ne"
    E = "e"
    SE = "se"
    S = "s"
    SW = "sw"
    W = "w"
    NW = "nw"

    @classmethod
    def from_string(cls, value: str):
        """Преобразует строку в элемент Enum"""
        for member in cls:
            if member.value == value.lower():
                return member
        return cls.N

    def to_vector(self) -> Tuple[float, float]:
        """Возвращает нормализованный вектор направления."""
        mapping = {
            "n": (0, -1),
            "ne": (0.707, -0.707),
            "e": (1, 0),
            "se": (0.707, 0.707),
            "s": (0, 1),
            "sw": (-0.707, 0.707),
            "w": (-1, 0),
            "nw": (-0.707, -0.707),
        }
        return mapping[self.value]


class MoveMixin(BaseMixin):
    def __init__(
        self,
        speed: float = 0.0,
        direction: Union[Direction, CompassDirection, str] = "left",
        boost: float = 300.0,
        move_freez: bool = False,
        move_mode: MoveModeType = MoveModeType.HORIZONTAL,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self._compass_direction = None
        self._direction_str = "left"
        self._direction_vector = (1.0, 0.0)
        self.speed = speed
        self._base_speed = speed
        self.boost = boost
        self.move_freez = move_freez
        self.move_mode = move_mode
        self._is_running = False

        if move_mode == MoveModeType.COMPASS:
            if isinstance(direction, CompassDirection):
                self._compass_direction = direction
            else:
                self._compass_direction = CompassDirection.from_string(str(direction))
        else:
            self.direction = direction

        self._direction_vector = (1.0, 0.0)

    @property
    def base_speed(self) -> float:
        return self._base_speed

    @property
    def direction(self):
        if self.move_mode == MoveModeType.COMPASS:
            return self._compass_direction.value
        return self._direction_str

    @direction.setter
    def direction(self, value):
        if self.move_mode == MoveModeType.COMPASS:
            if isinstance(value, CompassDirection):
                self._compass_direction = value
            else:
                self._compass_direction = CompassDirection.from_string(str(value))
        else:
            self._direction_str = value

    @property
    def is_running(self) -> bool:
        return self._is_running

    @is_running.setter
    def is_running(self, value: bool):
        if self.can_run():
            if value and not self._is_running:
                self.speed = self.base_speed + self.boost
            elif not value and self._is_running:
                self.speed = self.base_speed
            self._is_running = value
        else:
            self._is_running = False

    def can_run(self) -> bool:
        """Переопределить для дополнительных условий бега."""
        return True

    def can_move(self, new_x: float, new_y: float) -> bool:
        """Переопределить для проверки коллизий."""
        return True

    def on_move(self) -> None:
        """Вызывается при обычном движении."""
        pass

    def on_run(self) -> None:
        """Вызывается при беге."""
        pass

    def set_direction(self, direction: str) -> None:
        """Устанавливает направление (для горизонтального/вертикального режима)."""
        if self.move_mode in (MoveModeType.HORIZONTAL, MoveModeType.VERTICAL):
            self.direction = direction
        else:
            mapping = {"left": (-1, 0), "right": (1, 0), "up": (0, -1), "down": (0, 1)}
            if direction in mapping:
                dx, dy = mapping[direction]
                self._direction_vector = (dx, dy)
                self.direction = direction

    def set_direction_vector(self, dx: float, dy: float) -> None:
        """
        Устанавливает нормализованный вектор направления (для FREE режима).
        Если длина вектора равна нулю, вектор остаётся прежним.
        """
        length = (dx * dx + dy * dy) ** 0.5
        if length > 0:
            self._direction_vector = (dx / length, dy / length)
        vx, vy = self._direction_vector
        if abs(vx) > abs(vy):
            self.direction = "right" if vx > 0 else "left"
        else:
            self.direction = "down" if vy > 0 else "up"

    def set_compass_direction(self, direction: Union[CompassDirection, str]) -> None:
        """Устанавливает направление для режима COMPASS"""
        if self.move_mode != MoveModeType.COMPASS:
            raise ValueError("set_compass_direction() can only be used in COMPASS mode")
        if isinstance(direction, CompassDirection):
            self._compass_direction = direction
        else:
            self._compass_direction = CompassDirection.from_string(str(direction))

    def move(
        self, direction: Optional[str] = None, dt: Optional[float] = None
    ) -> Tuple[float, float]:
        """
        Перемещает объект в заданном направлении с учётом dt.

        Для режимов HORIZONTAL и VERTICAL:
            direction: 'left'/'right' или 'up'/'down'. Если не указан – используется self.direction.
        Для режима FREE:
            direction игнорируется; используется вектор, установленный через set_direction_vector().

        Args:
            direction: направление (строка).
            dt: дельта-время в секундах.

        Returns:
            (x, y) после перемещения.

        Raises:
            ValueError: если dt не передан или направление недопустимо.
        """
        if dt is None:
            raise ValueError("MoveMixin.move() requires dt argument")
        if self.move_freez:
            return (self.x, self.y)

        displacement = math.floor(self.speed * dt)
        dx = dy = 0.0

        if self.move_mode == MoveModeType.HORIZONTAL:
            dir_str = direction or self.direction
            if dir_str == "left":
                dx = -displacement
            elif dir_str == "right":
                dx = displacement
            else:
                if DEBUG:
                    raise ValueError(f"Invalid direction for HORIZONTAL mode: {dir_str}")
                return
            if dir_str != self.direction:
                self.direction = dir_str

        elif self.move_mode == MoveModeType.VERTICAL:
            dir_str = direction or self.direction
            if dir_str == "up":
                dy = -displacement
            elif dir_str == "down":
                dy = displacement
            else:
                if DEBUG:
                    raise ValueError(f"Invalid direction for VERTICAL mode: {dir_str}")
                return
            if dir_str != self.direction:
                self.direction = dir_str

        elif self.move_mode == MoveModeType.COMPASS:
            if direction is not None:
                self.set_compass_direction(direction)
            vx, vy = self._compass_direction.to_vector()
            dx = vx * displacement
            dy = vy * displacement

        elif self.move_mode == MoveModeType.FREE:
            vx, vy = self._direction_vector
            dx = vx * displacement
            dy = vy * displacement
            if abs(vx) > abs(vy):
                self.direction = "right" if vx > 0 else "left"
            else:
                self.direction = "down" if vy > 0 else "up"

        else:
            raise ValueError(f"Invalid direction: {dir_str}")

        new_x = self.x + dx
        new_y = self.y + dy
        if self.can_move(new_x, new_y):
            if self.is_running:
                self.on_run()
            else:
                self.on_move()
            self.x, self.y = new_x, new_y
        else:
            self.x, self.y = self.resolve_collision(new_x, new_y)

        return (self.x, self.y)

    def move_xy(self, dx: float, dy: float, dt: float) -> Tuple[float, float]:
        """
        Перемещает объект в направлении (dx, dy) (режим FREE).
        dx, dy — компоненты направления (могут быть любыми, нормализуются автоматически).
        Удобно для управления с клавиатуры (WASD/стик).

        Args:
            dx: смещение по X (нормализуется).
            dy: смещение по Y (нормализуется).
            dt: дельта-время.

        Returns:
            (x, y) после перемещения.
        """
        if self.move_mode != MoveModeType.FREE:
            if DEBUG:
                raise ValueError("move_xy() can only be used in FREE mode")
            return
        self.set_direction_vector(dx, dy)
        return self.move(dt=dt)

    def speed_boost(self, dt=None) -> None:
        """Включает бег."""
        self.is_running = True

    def stop_speed_boost(self, dt=None) -> None:
        """Выключает бег."""
        self.is_running = False

    def resolve_collision(self, new_x: int, new_y: int) -> tuple[int, int]:
        """
        Возвращает скорректированную позицию при столкновении (скользит по стенам).
        Пытается двигаться по X и Y по отдельности.
        """
