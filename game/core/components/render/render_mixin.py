from typing import Literal, Tuple
from pygame import Rect
from game.core.components.base.base_mixin import BaseMixin
from game.core.components.render.render_system import RenderSystem


class RenderMixin(BaseMixin):
    ''' Простой рендер фигуры на экран '''
    def __init__(
        self,
        color: Tuple[int, int, int] = (0, 0, 0),
        ignore_check: bool = False,
        display: bool = True,
        z_index: int = 1,
        position: Literal["absolut", "window"] = "absolut",
        destroy_on_render_exit: bool = False,
        padding: int | tuple[int, ...] | None = None,
        padding_top: int = 0,
        padding_right: int = 0,
        padding_bottom: int = 0,
        padding_left: int = 0,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.color = color
        self._ignore_render_check = ignore_check
        self.display = display
        self.z_index = z_index
        self.position = position
        self.destroy_on_render_exit = destroy_on_render_exit

        if padding is not None:
            if isinstance(padding, int):
                self._padding_top = padding
                self._padding_right = padding
                self._padding_bottom = padding
                self._padding_left = padding
            elif isinstance(padding, tuple):
                if len(padding) == 2:
                    self._padding_top = padding[0]
                    self._padding_right = padding[1]
                    self._padding_bottom = padding[0]
                    self._padding_left = padding[1]
                elif len(padding) == 4:
                    self._padding_top, self._padding_right, self._padding_bottom, self._padding_left = padding
        else:
            self._padding_top = padding_top
            self._padding_right = padding_right
            self._padding_bottom = padding_bottom
            self._padding_left = padding_left

        self._render_rect_dirty = True
        self._render_rect = Rect(0, 0, 0, 0)

        if self.auto_register:
            RenderSystem.register(self)

    @property
    def padding_top(self):
        return self._padding_top

    @padding_top.setter
    def padding_top(self, value):
        self._padding_top = value
        self._render_rect_dirty = True
        self._on_render_size_changed()

    @property
    def render_offset_x(self):
        return -self._padding_left

    @property
    def render_offset_y(self):
        return -self._padding_top

    @property
    def render_width(self):
        return self.width + self._padding_left + self._padding_right

    @property
    def render_height(self):
        return self.height + self._padding_top + self._padding_bottom

    @property
    def ignore_render_check(self):
        return self._ignore_render_check
    
    @property
    def z_index(self):
        return self._z_index

    @z_index.setter
    def z_index(self, value):
        self._z_index = value
        RenderSystem.invalidate_cache()

    def destroy(self) -> None:
        RenderSystem.destroy(self)
        return super().destroy()

    def update_before_render(self) -> None:
        pass

    def update_after_render(self) -> None:
        pass

    def on_exit_render_zone(self) -> None:
        ''' Обработичк, если объект вышел из зоны рендера '''
        pass

    def on_render_size_changed(self):
        pass

    def prepare_to_render(self, camera):
        ''' Подготовка данных к рендерингу '''
        screen_pos = camera.apply((self.x - self._padding_left,
                                   self.y - self._padding_top))
        return {
            'type': 'rect',
            'data': (self.color,
                     Rect(*screen_pos,
                          self.width + self._padding_left + self._padding_right,
                          self.height + self._padding_top + self._padding_bottom)),
        }