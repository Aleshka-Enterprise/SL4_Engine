from typing import Tuple

from game.core.components.base.base_mixin import BaseMixin
from game.core.components.render import RenderSystem
from pygame import Rect


class Camera:
    """Камера, следующая за целью с плавностью и зоной рендеринга"""

    MAX_LEVEL_HEIGHT = 100_000
    MAX_LEVEL_WIDTH = 100_000

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        target: BaseMixin | None = None,
        use_horizontal_look_ahead: bool = True,
        use_vertical_look_ahead: bool = False,
        smooth_time: float = 0.3,
        look_ahead_time: float = 0.1,
        look_ahead_offset: float = 80.0,  # опережение по направлению движения
        padding = 1000,                   # отступ для зоны рендеринга
        **kwargs,
    ):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.viewport = Rect(0, 0, screen_width, screen_height)
        self.padding = padding
        self._render_zone = Rect(0, 0, 0, 0)
        self.target = target

        self.deadzone = Rect(
            screen_width // 4, screen_height // 4, screen_width // 2, screen_height // 2
        )

        self.look_ahead_offset = look_ahead_offset
        self.current_offset_x = 0.0
        self.current_offset_y = 0.0
        self._prev_x = 0.0
        self._prev_y = 0.0
        self.use_horizontal_look_ahead = use_horizontal_look_ahead
        self.use_vertical_look_ahead = use_vertical_look_ahead
        self.smooth_time = smooth_time
        self.look_ahead_time = look_ahead_time

    @property
    def render_zone(self):
        return self._render_zone

    def _update_render_zone(self) -> Rect:
        """Обновляет зону рендеринга, если текущий viewport вышел за её границы."""
        if not self.render_zone.contains(self.viewport):
            x = self.viewport.x - self.padding
            y = self.viewport.y - self.padding
            width = self.screen_width + (self.padding * 2)
            height = self.screen_height + (self.padding * 2)
            self._render_zone = Rect(x, y, width, height)
            RenderSystem.update_render_objects()
        return self._render_zone
    
    def _update_look_ahead(self, dt: float) -> None:
        """Обновляем опережение"""
        dx = self.target.x - self._prev_x
        dy = self.target.y - self._prev_y
        self._prev_x, self._prev_y = self.target.x, self.target.y

        target_offset_x = self.look_ahead_offset if dx > 0 else (-self.look_ahead_offset if dx < 0 else 0.0)
        target_offset_y = self.look_ahead_offset if dy > 0 else (-self.look_ahead_offset if dy < 0 else 0.0)

        if self.look_ahead_time > 0:
            factor = 1 - (0.001 ** (dt / self.look_ahead_time))
            self.current_offset_x += (target_offset_x - self.current_offset_x) * factor
            if self.use_vertical_look_ahead:
                self.current_offset_y += (target_offset_y - self.current_offset_y) * factor
        else:
            self.current_offset_x = target_offset_x
            self.current_offset_y = target_offset_y

    def _calculate_target_position(self) -> tuple[float, float]:
        target = self.target
        vp = self.viewport

        target_x = vp.x
        target_y = vp.y

        if target.x < vp.x + self.deadzone.left:
            target_x = target.x - self.deadzone.left
        elif target.x + target.width > vp.x + self.deadzone.right:
            target_x = target.x + target.width - self.deadzone.right

        if target.y < vp.y + self.deadzone.top:
            target_y = target.y - self.deadzone.top
        elif target.y + target.height > vp.y + self.deadzone.bottom:
            target_y = target.y + target.height - self.deadzone.bottom

        # Добавляем опережение
        target_x += self.current_offset_x
        target_y += self.current_offset_y

        target_x = max(0, min(target_x, self.MAX_LEVEL_WIDTH - self.screen_width))
        target_y = max(0, min(target_y, self.MAX_LEVEL_HEIGHT - self.screen_height))

        return target_x, target_y
    
    def _apply_smoothing(self, dt: float, target_x: float, target_y: float) -> None:
        """Применяем сглаживание к viewport"""
        if self.smooth_time > 0:
            factor = 1 - (0.001 ** (dt / self.smooth_time))
            self.viewport.x += (target_x - self.viewport.x) * factor
            self.viewport.y += (target_y - self.viewport.y) * factor
        else:
            self.viewport.x = target_x
            self.viewport.y = target_y

    def update(self, dt: float):
        if not self.target:
            return

        self._update_look_ahead(dt)
        target_x, target_y = self._calculate_target_position()
        self._apply_smoothing(dt, target_x, target_y)
        self._update_render_zone()

    def apply(self, pos) -> Tuple[float, float]:
        """Преобразует глобальные координаты в экранные"""
        return (pos[0] - self.viewport.x, pos[1] - self.viewport.y)
