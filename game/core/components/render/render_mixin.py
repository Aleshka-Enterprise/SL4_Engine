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
        **kwargs
    ):
        super().__init__(**kwargs)

        self.color = color
        self._ignore_render_check = ignore_check
        self.display = display
        self.z_index = z_index
        self.position = position
        self.destroy_on_render_exit = destroy_on_render_exit

        if self.auto_register:
            RenderSystem.register(self)

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

    def prepare_to_render(self, camera):
        ''' Подготовка данных к рендерингу '''
        screen_pos = camera.apply((self.x, self.y))
        return {
            'type': 'rect',
            'data': (self.color, Rect(*screen_pos, self.width, self.height)),
        }

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
