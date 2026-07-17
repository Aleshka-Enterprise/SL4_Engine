from typing import Literal, Tuple

from game.core.components.base.base_mixin import BaseMixin
from game.core.components.render.render_system import RenderSystem
from game.core.components.render.render_types import RenderComand, RenderType
from pygame import Rect


class RenderMixin(BaseMixin):
    """Простой рендер фигуры на экран"""

    def __init__(
        self,
        color: Tuple[int, int, int] = (0, 0, 0),
        ignore_render_check: bool = False,
        display: bool = True,
        z_index: int = 1,
        position: Literal["world", "window"] = "world",
        destroy_on_render_exit: bool = False,
        padding: int | tuple[int, ...] | None = None,
        padding_top: int = 0,
        padding_right: int = 0,
        padding_bottom: int = 0,
        padding_left: int = 0,
        flip_x: bool = False,
        flip_y: bool = False,
        rotation: float = 0.0,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.color = color
        self._ignore_render_check = ignore_render_check
        self.display = display
        self.z_index = z_index
        self.position = position
        self.destroy_on_render_exit = destroy_on_render_exit
        self._flip_x = bool(flip_x)
        self._flip_y = bool(flip_y)
        self._rotation = rotation

        if padding is not None:
            if isinstance(padding, int):
                self._padding_top = padding
                self._padding_right = padding
                self._padding_bottom = padding
                self._padding_left = padding
            elif isinstance(padding, tuple) or isinstance(padding, list):
                if len(padding) == 2:
                    self._padding_top = padding[0]
                    self._padding_right = padding[1]
                    self._padding_bottom = padding[0]
                    self._padding_left = padding[1]
                elif len(padding) == 4:
                    (
                        self._padding_top,
                        self._padding_right,
                        self._padding_bottom,
                        self._padding_left,
                    ) = padding
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

    @property
    def padding_bottom(self):
        return self._padding_bottom

    @padding_bottom.setter
    def padding_bottom(self, value):
        self._padding_bottom = value
        self._render_rect_dirty = True

    @property
    def padding_left(self):
        return self._padding_left

    @padding_left.setter
    def padding_left(self, value):
        self._padding_left = value
        self._render_rect_dirty = True

    @property
    def padding_right(self):
        return self._padding_right

    @padding_right.setter
    def padding_right(self, value):
        self._padding_right = value
        self._render_rect_dirty = True

    @property
    def flip_x(self):
        return self._flip_x

    @flip_x.setter
    def flip_x(self, value):
        self._flip_x = bool(value)
        self._on_transform_changed()

    @property
    def flip_y(self):
        return self._flip_y

    @flip_y.setter
    def flip_y(self, value):
        self._flip_y = bool(value)
        self._on_transform_changed()

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        self._rotation = float(value) % 360.0
        self._on_transform_changed()

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

    def update_before_render(self, dt) -> None:
        """Вызывается перед рендером"""
        pass

    def update_after_render(self, dt) -> None:
        """Вызывается после рендера"""
        pass

    def on_exit_render_zone(self) -> None:
        """Обработичк, если объект вышел из зоны рендера"""
        pass

    def on_render_size_changed(self):
        """Вызывается при изменении размера"""
        pass

    def _on_transform_changed(self):
        self._transform_cache_dirty = True
        self._render_rect_dirty = True
        self.invalidate_scaled_cache()

    def prepare_to_render(self, camera):
        """Подготовка данных к рендерингу"""
        if self.position == "window":
            screen_pos = (self.x, self.y)
        elif self.position == "world":
            screen_pos = camera.apply((self.x - self._padding_left, self.y - self._padding_top))
        rect = Rect(
            *screen_pos,
            self.width + self._padding_left + self._padding_right,
            self.height + self._padding_top + self._padding_bottom,
        )
        return [RenderComand(type=RenderType.RECT, data={"color": self.color, "rect": rect})]

    def invalidate_scaled_cache(self):
        pass
