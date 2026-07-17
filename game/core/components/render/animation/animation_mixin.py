import os
import random
from typing import Dict, List, Optional, Tuple

import pygame
from game.core.components.render.render_mixin import RenderMixin
from game.core.components.render.render_types import RenderComand, RenderType


class AnimationMixin(RenderMixin):
    # Кэш оригинальных кадров (без масштабирования), общий для всех экземпляров
    _loaded_frames: Dict[str, List[pygame.Surface]] = {}

    def __init__(
        self,
        sprites_root: Optional[str] = None,
        animations: Optional[Dict[str, dict]] = None,
        current_animation: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        if sprites_root is None:
            try:
                module_file = self.__class__.__module__.replace(".", "/") + ".py"
                base_dir = os.path.dirname(os.path.abspath(module_file))
                sprites_root = os.path.join(base_dir, "sprites")
            except Exception:
                sprites_root = ""
        self.sprites_root = sprites_root

        self.animations_config = animations or {}
        self.current_state: Optional[str] = None
        self.current_frame_index: int = 0
        self._frames: List[pygame.Surface] = []
        self._animation_timer: float = 0.0
        self._timer: int = 6
        self._mode: str = "loop"
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
                f for f in os.listdir(folder) if f.lower().endswith((".png", ".jpg", ".bmp"))
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

    def play_animation(
        self,
        state: str,
        mode: Optional[str] = None,
        timer: Optional[int] = None,
        reset: bool = True,
    ):
        if state != self.current_state:
            self._frames = self.load_state_frames(state)
            self.current_state = state
            if reset:
                self.current_frame_index = 0
                self._animation_timer = 0.0

        state_config = self.animations_config.get(state, {})
        self._mode = mode or state_config.get("mode", "loop")
        self._timer = timer or state_config.get("timer")
        self._playing = True

    def stop(self):
        self._playing = False

    def get_current_frame(self) -> Optional[pygame.Surface]:
        if not self._frames:
            return None
        return self._frames[self.current_frame_index]

    def update_animation(self, dt):
        if not self._playing or not self._frames or self._timer is None:
            return

        self._animation_timer += dt
        frame_duration = self._timer

        while self._animation_timer >= frame_duration:
            self._animation_timer -= frame_duration
            if self._mode == "loop":
                self.current_frame_index = (self.current_frame_index + 1) % len(self._frames)
            elif self._mode == "once":
                if self.current_frame_index < len(self._frames) - 1:
                    self.current_frame_index += 1
                else:
                    self.stop()
                    break
            elif self._mode == "random":
                self.current_frame_index = random.randint(0, len(self._frames) - 1)
            elif self._mode == "freeze":
                break

    def _get_scaled_frame(
        self, state: str, frame_index: int, width: int, height: int
    ) -> pygame.Surface:
        """Возвращает кадр с применёнными масштабом, отражением и поворотом."""
        # Ключ кэша теперь включает параметры трансформации
        key = (state, frame_index, width, height, self.flip_x, self.flip_y, self.rotation)
        if key in self._scaled_cache:
            return self._scaled_cache[key]

        original_frames = self._loaded_frames.get(os.path.join(self.sprites_root, state))
        if not original_frames or frame_index >= len(original_frames):
            # Возвращаем заглушку, если кадр не найден
            placeholder = pygame.Surface((width, height), pygame.SRCALPHA)
            placeholder.fill((255, 0, 255, 128))
            self._scaled_cache[key] = placeholder
            return placeholder

        original = original_frames[frame_index]

        scaled = pygame.transform.scale(original, (width, height))

        if self.flip_x or self.flip_y:
            scaled = pygame.transform.flip(scaled, self.flip_x, self.flip_y)

        if self.rotation != 0.0:
            scaled = pygame.transform.rotate(scaled, self.rotation)

        self._scaled_cache[key] = scaled
        return scaled

    def invalidate_scaled_cache(self):
        if hasattr(self, "_scaled_cache"):
            self._scaled_cache.clear()
        if self.current_state and self._frames:
            self._scaled_cache = {}

    def on_render_size_changed(self):
        """Вызывается из RenderMixin при изменении padding или других параметров,
        влияющих на визуальный размер."""
        self.invalidate_scaled_cache()

    def prepare_to_render(self, camera):
        if self.current_state and self._frames:
            screen_pos = camera.apply(
                (self.x + self.render_offset_x, self.y + self.render_offset_y)
            )
            screen_pos = (int(round(screen_pos[0])), int(round(screen_pos[1])))

            scaled_frame = self._get_scaled_frame(
                self.current_state, self.current_frame_index, self.render_width, self.render_height
            )
            center_x = screen_pos[0] + self.render_width / 2.0
            center_y = screen_pos[1] + self.render_height / 2.0
            rect = scaled_frame.get_rect(center=(center_x, center_y))

            res = RenderComand(type=RenderType.IMAGE, data={"surface": scaled_frame, "rect": rect})
            return [res]

        return super().prepare_to_render(camera)

    def update_before_render(self, dt):
        res = super().update_before_render(dt)
        self.update_animation(dt)
        return res

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        if self._width != value:
            self._width = value
            self.invalidate_scaled_cache()
            self._render_rect_dirty = True

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        if self._height != value:
            self._height = value
            self.invalidate_scaled_cache()
            self._render_rect_dirty = True
