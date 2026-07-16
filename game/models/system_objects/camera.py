from pygame import Rect
from game.core.components.base.base_mixin import BaseMixin
from game.core.components.utils.timer import TimerMixin
from game.core.components.render import RenderSystem


class Camera(TimerMixin):
    """
    Камера с мёртвой зоной (deadzone), плавным следованием и опережением (look-ahead).

    Особенности:
        - Deadzone центрирована и занимает ½ ширины и ½ высоты экрана.
        - Плавная интерполяция положения камеры (smooth_speed).
        - Опережение в сторону движения (look-ahead) для лучшего обзора.
        - Автоматическое обновление render_zone (зоны видимости) для оптимизации рендеринга.
        - Поддержка горизонтального и опционально вертикального look-ahead.

    Attributes:
        screen_width (int): Ширина экрана в пикселях.
        screen_height (int): Высота экрана в пикселях.
        viewport (Rect): Текущая видимая область (мировые координаты).
        deadzone (Rect): Прямоугольник (экранные координаты), внутри которого цель может двигаться без смещения камеры.
        smooth_speed (float): Скорость интерполяции (0.0 – мгновенно, 1.0 – бесконечно медленно).
        look_ahead_offset (float): Максимальное смещение вперёд в пикселях.
        look_ahead_speed (float): Скорость нарастания/затухания опережения.
        current_offset_x (float): Текущее горизонтальное опережение (плавно меняется).
        current_offset_y (float): Текущее вертикальное опережение.
        padding (int): Отступ вокруг viewport для вычисления render_zone.
        target (BaseMixin | None): Объект, за которым следит камера (обычно игрок).
        use_horizontal_look_ahead (bool): Включено ли горизонтальное опережение.
        use_vertical_look_ahead (bool): Включено ли вертикальное опережение.
    """
    MAX_LEVEL_HEIGHT = 100_000
    MAX_LEVEL_WIDTH = 100_000

    def __init__(self,
                 screen_width: int,
                 screen_height: int,
                 target: BaseMixin | None = None,
                 use_horizontal_look_ahead: bool = True,
                 use_vertical_look_ahead: bool = False,
                 smooth_speed: float = 0.2,
                 look_ahead_offset: float = 100.0,
                 look_ahead_speed: float = 0.05,
                 smooth_time: float = 0.3,
                 look_ahead_time: float = 0.1,
                 **kwargs
                ):
        '''
        Инициализация камеры.

        Args:
            screen_width (int): Ширина окна.
            screen_height (int): Высота окна.
            target (BaseMixin | None, optional): Целевой объект (игрок). По умолчанию None.
            use_horizontal_look_ahead (bool, optional): Включить горизонтальное опережение. По умолчанию True.
            use_vertical_look_ahead (bool, optional): Включить вертикальное опережение. По умолчанию False.
            smooth_speed (float, optional): Скорость интерполяции (чем меньше, тем плавнее). По умолчанию 0.2.
            look_ahead_offset (float, optional): Максимальное смещение опережения. По умолчанию 100.0.
            look_ahead_speed (float, optional): Скорость изменения опережения. По умолчанию 0.05.
            **kwargs: Пробрасываются в родительские классы (TimerMixin).
        '''
        super().__init__(**kwargs)

        self.screen_width = screen_width
        self.screen_height = screen_height
        self.viewport = Rect(0, 0, screen_width, screen_height)
        self.padding = 1000
        self._render_zone = Rect(0, 0, 0, 0)
        self.target = target

        self.deadzone = Rect(
            screen_width // 4,
            screen_height // 4,
            screen_width // 2,
            screen_height // 2
        )

        self.smooth_speed = smooth_speed

        self.look_ahead_offset = look_ahead_offset
        self.look_ahead_speed = look_ahead_speed
        self.current_offset_x = 0.0
        self.current_offset_y = 0.0
        self._prev_x = 0.0
        self._prev_y = 0.0
        self.use_horizontal_look_ahead = use_horizontal_look_ahead
        self.use_vertical_look_ahead = use_vertical_look_ahead
        self.smooth_time = smooth_time
        self.look_ahead_time = look_ahead_time

        self.add_timer(
            [self.update_render_zone],
            loop=True,
            seconds=0.1
        )

    @property
    def render_zone(self):
        return self._render_zone

    def update_render_zone(self) -> Rect:
        '''
        Обновляет зону рендеринга, если текущий viewport вышел за её границы.

        Зона рендеринга – это viewport, расширенный на padding со всех сторон.
        При изменении зоны уведомляет RenderSystem о необходимости пересчитать список объектов для отрисовки.

        Returns:
            Rect: Актуальная зона рендеринга.
        '''
        if not self.render_zone.contains(self.viewport):
            x = self.viewport.x - self.padding
            y = self.viewport.y - self.padding
            width = self.screen_width + (self.padding * 2)
            height = self.screen_height + (self.padding * 2)
            self._render_zone = Rect(x, y, width, height)
            RenderSystem.update_render_objects()
        return self._render_zone

    def update(self, dt: float):
        if not self.target:
            return

        target = self.target

        dx = target.x - self._prev_x
        dy = target.y - self._prev_y
        self._prev_x = target.x
        self._prev_y = target.y

        target_offset_x = self.look_ahead_offset if dx > 0 else -self.look_ahead_offset if dx < 0 else 0.0
        target_offset_y = self.look_ahead_offset if dy > 0 else -self.look_ahead_offset if dy < 0 else 0.0


        if self.look_ahead_time > 0:
            factor = 1 - (0.001 ** (dt / self.look_ahead_time))
            self.current_offset_x += (target_offset_x - self.current_offset_x) * factor
            if self.use_vertical_look_ahead:
                self.current_offset_y += (target_offset_y - self.current_offset_y) * factor
        else:
            self.current_offset_x = target_offset_x
            self.current_offset_y = target_offset_y

        target_x = self.viewport.x
        target_y = self.viewport.y

        if target.x < self.viewport.x + self.deadzone.left:
            target_x = target.x - self.deadzone.left
        elif target.x + target.width > self.viewport.x + self.deadzone.right:
            target_x = target.x + target.width - self.deadzone.right

        if target.y < self.viewport.y + self.deadzone.top:
            target_y = target.y - self.deadzone.top
        elif target.y + target.height > self.viewport.y + self.deadzone.bottom:
            target_y = target.y + target.height - self.deadzone.bottom

        target_x += self.current_offset_x
        target_y += self.current_offset_y

        target_x = max(0, min(target_x, self.MAX_LEVEL_WIDTH - self.screen_width))
        target_y = max(0, min(target_y, self.MAX_LEVEL_HEIGHT - self.screen_height))

        if self.smooth_time > 0:
            factor = 1 - (0.001 ** (dt / self.smooth_time))
            self.viewport.x += (target_x - self.viewport.x) * factor
            self.viewport.y += (target_y - self.viewport.y) * factor
        else:
            self.viewport.x = target_x
            self.viewport.y = target_y

    def apply(self, pos) -> None:
        '''Преобразует глобальные координаты в экранные'''
        return (pos[0] - self.viewport.x, pos[1] - self.viewport.y)
