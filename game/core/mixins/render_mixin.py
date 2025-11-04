from typing import Tuple
from pygame import Rect
from game.core.mixins.base_mixin import BaseMixin
from game.core.systems.render_system import RenderSystem


class RenderMixin(BaseMixin):
    def __init__(
        self,
        color: Tuple[int, int, int] = (0, 0, 0),
        ignore_check: bool = False,
        auto_register_in_render_system: bool = True,
        display: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.color = color
        self._ignore_render_check = ignore_check
        self.display = display
        
        if auto_register_in_render_system:
            RenderSystem.register(self)
            
    @property
    def render_layer(self) -> str:
        ''' Название слоя. Нужно для правильной очереди отрисовки. '''
        return 'base'
            
    @property
    def ignore_render_check(self):
        return self._ignore_render_check
        
    @property
    def render_layer(self) -> str:
        return 'entity'
        
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