import os
import random
from typing import Dict, List, Optional
import pygame
from pygame import Rect
from game.core.components.render.render_mixin import RenderMixin


class AnimationMixin(RenderMixin):
    # Кэш кадров, общий для всех экземпляров (ключ — путь к папке состояния)
    _loaded_frames: Dict[str, List[pygame.Surface]] = {}

    def __init__(
        self,
        sprites_root: Optional[str] = None,
        animations: Optional[Dict[str, dict]] = None,
        current_animation: Optional[str] = None,
        **kwargs
    ):
        """
        :param sprites_root: путь к папке sprites/ относительно файла модели.
        :param animations: словарь с настройками состояний, например:
                           {'idle': {'fps': 6, 'mode': 'loop'}}
        :param current_animation: имя начального состояния (если нужно сразу запустить)
        Остальные параметры (x, y, color, z_index...) передаются в RenderMixin.
        """
        super().__init__(**kwargs)

        # Определяем корень спрайтов
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
        self._mode: str = 'loop'   # loop, once, random, freeze
        self._playing: bool = False

        # Если передано начальное состояние – сразу запускаем
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

    def prepare_to_render(self, camera):
        """Если есть активный кадр – отдаём изображение, иначе – прямоугольник из RenderMixin."""
        if self.current_state and self.get_current_frame():
            screen_pos = camera.apply((self.x, self.y))
            frame = self.get_current_frame()
            # масштабируем под текущий размер объекта, если нужно
            if frame.get_size() != (self.width, self.height):
                frame = pygame.transform.scale(frame, (self.width, self.height))
            return {
                'type': 'image',
                'data': (frame, Rect(*screen_pos, self.width, self.height))
            }

        return super().prepare_to_render(camera)

    def update_before_render(self, dt: float = 0.0):
        """Вызывается каждый кадр, чтобы обновить кадр анимации."""
        if dt > 0:
            self.update_animation(dt)
