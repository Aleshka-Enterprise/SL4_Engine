from pygame import Rect
from game.core import storage
from game.core.mixins.timer_mixin import TimerMixin
from game.core.systems.render_system import RenderSystem


class Camera(TimerMixin):
    def __init__(self, screen_width: int, screen_height: int, **kwargs):
        super().__init__(**kwargs)

        self.screen_width = screen_width
        self.screen_height = screen_height
        self.viewport = Rect(0, 0, screen_width, screen_height)
        self.padding = 1000
        self._render_zone = Rect(0, 0, 0, 0)
        self.target = None

        self.deadzone = Rect(
            screen_width // 6,   # Отступ слева (1/6 экрана)
            screen_height // 6,  # Отступ сверху (1/6 экрана)
            screen_width // 3,
            screen_height // 2
        )

        self.add_timer(
            [self.update_render_zone],
            loop=True,
            frames=5
        )

        storage.camera = self

    @property
    def render_zone(self):
        return self._render_zone

    def update_render_zone(self) -> Rect:
        if not self.render_zone.contains(self.viewport):
            x = self.viewport.x - self.padding
            y = self.viewport.y - self.padding
            width = self.screen_width + (self.padding * 2)
            height = self.screen_height + (self.padding * 2)
            self._render_zone = Rect(x, y, width, height)
            RenderSystem.update_render_objects()
        return self._render_zone

    def update(self, target):
        if not target:
            return

        # Горизонтальное движение
        if target.x < self.viewport.x + self.deadzone.left:
            self.viewport.x = target.x - self.deadzone.left
        elif target.x + target.width > self.viewport.x + self.deadzone.right:
            self.viewport.x = target.x + target.width - self.deadzone.right

        # Вертикальное движение
        if target.y < self.viewport.y + self.deadzone.top:
            self.viewport.y = target.y - self.deadzone.top
        elif target.y + target.height > self.viewport.y + self.deadzone.bottom:
            self.viewport.y = target.y + target.height - self.deadzone.bottom

        # Ограничение камеры границами уровня (если нужно)
        self.viewport.x = max(0, min(self.viewport.x, 100000 - self.screen_width))
        self.viewport.y = max(0, min(self.viewport.y, 100000 - self.screen_height))

    def apply(self, pos) -> None:
        '''Преобразует глобальные координаты в экранные'''
        return (pos[0] - self.viewport.x, pos[1] - self.viewport.y)
