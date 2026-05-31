import os
import random
from typing import Dict, List, Optional, Tuple
import pygame
from pygame import Rect
from game.core.components.render.render_mixin import RenderMixin


class AnimationMixin(RenderMixin):
    # Кэш оригинальных кадров (без масштабирования), общий для всех экземпляров
    _loaded_frames: Dict[str, List[pygame.Surface]] = {}

    def __init__(
        self,
        sprites_root: Optional[str] = None,
        animations: Optional[Dict[str, dict]] = None,
        current_animation: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if sprites_root is None:
            try:
                module_file = self.__class__.__module__.replace('.', '/') + '.py'
                base_dir = os.path.dirname(os.path.abspath(module_file))
                sprites_root = os.path.join(base_dir, 'sprites')
            except Exception:
                sprites_root = ''
        self.sprites_root = sprites_root

        self.animations_config = animations or {}
        self.current_state: Optional[str] = None
        self.current_frame_index: int = 0
        self._frames: List[pygame.Surface] = []
        self._animation_timer: float = 0.0
        self._fps: int = 6
        self._mode: str = 'loop'
        self._playing: bool = False

        # Кэш масштабированных кадров для этого экземпляра
        # Ключ: (state, frame_index, width, height) -> pygame.Surface
        self._scaled_cache: Dict[Tuple[str, int, int, int], pygame.Surface] = {}

        if current_animation:
            self.play_animation(current_animation)

    def load_state_frames(self, state: str) -> List[pygame.Surface]:
        folder = os.path.join(self.sprites_root, state)
        if folder in self._loaded_frames:
            return self._loaded_frames[folder]

        frames = []
        if os.path.isdir(folder):
            files = sorted(
                f for f in os.listdir(folder)
                if f.lower().endswith(('.png', '.jpg', '.bmp'))
            )
            for fname in files:
                path = os.path.join(folder, fname)
                try:
                    img = pygame.image.load(path).convert_alpha()
                    frames.append(img)
                except pygame.error:
                    continue
        self._loaded_frames[folder] = frames
        return frames

    def play_animation(self, state: str, mode: Optional[str] = None,
             fps: Optional[int] = None, reset: bool = True):
        if state != self.current_state:
            self._frames = self.load_state_frames(state)
            self.current_state = state
            if reset:
                self.current_frame_index = 0
                self._animation_timer = 0.0

        state_config = self.animations_config.get(state, {})
        self._mode = mode or state_config.get('mode', 'loop')
        self._fps = fps or state_config.get('fps', 6)
        self._playing = True

    def stop(self):
        self._playing = False

    def get_current_frame(self) -> Optional[pygame.Surface]:
        if not self._frames:
            return None
        return self._frames[self.current_frame_index]

    def update_animation(self, dt: float):
        if not self._playing or not self._frames:
            return

        self._animation_timer += dt
        frame_duration = 1.0 / self._fps

        while self._animation_timer >= frame_duration:
            self._animation_timer -= frame_duration
            if self._mode == 'loop':
                self.current_frame_index = (self.current_frame_index + 1) % len(self._frames)
            elif self._mode == 'once':
                if self.current_frame_index < len(self._frames) - 1:
                    self.current_frame_index += 1
                else:
                    self.stop()
                    break
            elif self._mode == 'random':
                self.current_frame_index = random.randint(0, len(self._frames) - 1)
            elif self._mode == 'freeze':
                break

    def _get_scaled_frame(self, state: str, frame_index: int, width: int, height: int) -> pygame.Surface:
        """Возвращает масштабированный кадр, используя кэш"""
        key = (state, frame_index, width, height)
        if key not in self._scaled_cache:
            original = self._loaded_frames.get(os.path.join(self.sprites_root, state), [])[frame_index]
            scaled = pygame.transform.scale(original, (width, height))
            self._scaled_cache[key] = scaled
        return self._scaled_cache[key]

    def invalidate_scaled_cache(self):
        """Вызывать при изменении ширины/высоты объекта"""
        self._scaled_cache.clear()
        if self.current_state and self._frames:
            self._scaled_cache = {}

    def prepare_to_render(self, camera):
        """Если есть активный кадр – отдаём изображение, иначе – прямоугольник из RenderMixin."""
        if self.current_state and self._frames:
            screen_pos = camera.apply((self.x, self.y))
            # Берём масштабированный кадр из кэша (или создаём)
            scaled_frame = self._get_scaled_frame(
                self.current_state,
                self.current_frame_index,
                self.width,
                self.height
            )
            return {
                'type': 'image',
                'data': (scaled_frame, Rect(*screen_pos, self.width, self.height))
            }
        return super().prepare_to_render(camera)

    def update_before_render(self, dt: float = 0.0):
        if dt > 0:
            self.update_animation(dt)

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        if self._width != value:
            self._width = value
            self.invalidate_scaled_cache()

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        if self._height != value:
            self._height = value
            self.invalidate_scaled_cache()
