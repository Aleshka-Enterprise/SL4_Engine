import os
from typing import Optional, Tuple
import pygame
from game.core.components.render.render_mixin import RenderMixin
from game.core.components.render.render_types import RenderComand, RenderType

class TextMixin(RenderMixin):
    _font_cache: dict = {}

    def __init__(
        self,
        text: str = "",
        font_name: Optional[str] = None,
        font_size: int = 24,
        text_color: Optional[Tuple[int, int, int]] = None,
        antialias: bool = True,
        fonts_root: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)

        self._text = text
        self._font_name = font_name
        self._font_size = font_size
        self._text_color = text_color if text_color is not None else self.color
        self._antialias = antialias
        self._ignore_render_check = True
        self.display = True

        if fonts_root is None:
            try:
                module_file = self.__class__.__module__.replace('.', '/') + '.py'
                base_dir = os.path.dirname(os.path.abspath(module_file))
                fonts_root = os.path.join(base_dir, 'fonts')
            except Exception:
                fonts_root = ''
        self.fonts_root = fonts_root

        # Загружаем шрифт и создаём начальную текстовую поверхность
        self._font = self._load_font(self._font_name, self._font_size)
        self._rendered_surface = None
        self._render_text()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        if self._text != value:
            self._text = value
            self._render_text()

    @property
    def font_name(self):
        return self._font_name

    @font_name.setter
    def font_name(self, value):
        if self._font_name != value:
            self._font_name = value
            self._font = self._load_font(value, self._font_size)
            self._render_text()

    @property
    def font_size(self):
        return self._font_size

    @font_size.setter
    def font_size(self, value):
        if self._font_size != value:
            self._font_size = value
            self._font = self._load_font(self._font_name, value)
            self._render_text()

    @property
    def text_color(self):
        return self._text_color

    @text_color.setter
    def text_color(self, value):
        if self._text_color != value:
            self._text_color = value
            self._render_text()

    @property
    def antialias(self):
        return self._antialias

    @antialias.setter
    def antialias(self, value):
        if self._antialias != value:
            self._antialias = value
            self._render_text()

    def _load_font(self, font_name: Optional[str], size: int) -> pygame.font.Font:
        """Загружает шрифт (из fonts_root или системный) с кэшированием."""
        if font_name is None:
            return pygame.font.Font(None, size)
        font_path = os.path.join(self._get_fonts_root_static(), font_name)
        key = (font_path, size)
        if key not in self._font_cache:
            try:
                self._font_cache[key] = pygame.font.Font(font_path, size)
            except Exception:
                self._font_cache[key] = pygame.font.SysFont(font_name, size)
        return self._font_cache[key]

    def _get_fonts_root_static(self):
        module_file = self.__class__.__module__.replace('.', '/') + '.py'
        base_dir = os.path.dirname(os.path.abspath(module_file))
        return base_dir + '\\fonts'

    def _load_font_instance(self, font_name: Optional[str], size: int) -> pygame.font.Font:
        if font_name is None:
            return pygame.font.Font(None, size)
        font_path = os.path.join(self.fonts_root, font_name)
        key = (font_path, size)
        if key not in TextMixin._font_cache:
            try:
                TextMixin._font_cache[key] = pygame.font.Font(font_path, size)
            except Exception:
                TextMixin._font_cache[key] = pygame.font.SysFont(font_name, size)
        return TextMixin._font_cache[key]

    def _render_text(self):
        """Создаёт (или обновляет) отрендеренную поверхность текста."""
        if not self._font:
            self._rendered_surface = pygame.Surface((0, 0))
            return
        self._rendered_surface = self._font.render(
            self._text, self._antialias, self.text_color
        )

    def prepare_to_render(self, camera):
        if self._rendered_surface is None:
            self._render_text()

        screen_pos = camera.apply((self.x, self.y))
        text_rect = self._rendered_surface.get_rect()
        text_rect.topleft = screen_pos

        return [
            RenderComand(
                type=RenderType.TEXT,
                data={ 'surface': self._rendered_surface, 'rect': text_rect }
            )
        ]
