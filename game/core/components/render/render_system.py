import pygame
from game.core.components.base.base_system import BaseSystem
from game.settings import DISPLAY, DEBUG, WINDOW_CAPTION
from game.core.storage import storage
from game.core.components.phisics.collision import CollisionSystem
from game.core.components.gameplay.event import EventsSystem


class RenderSystem(BaseSystem):
    pygame.font.init()

    _window: pygame.Surface | None = None
    _debug_font = pygame.font.SysFont('Comic Sans MS', 30)
    _current_fps = 0
    is_freezable = False

    @classmethod
    def init_window(cls) -> pygame.Surface:
        '''Инициализация окна pygame'''
        if cls._window:
            return cls._window

        width = DISPLAY.WIDTH
        height = DISPLAY.HEIGHT
        window = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        pygame.display.set_caption(WINDOW_CAPTION)
        cls._window = window
        return window

    @classmethod
    def set_surrent_fps(cls, value) -> None:
        cls._current_fps = value

    @classmethod
    def _render_rect_batch(cls, commands) -> None:
        """Пакетная отрисовка прямоугольников"""
        if not commands:
            return

        for color, rect in commands:
            pygame.draw.rect(cls._window, color, rect)

    @classmethod
    def _render_circle_batch(cls, commands):
        if not commands:
            return

        for color, x, y, radius in commands:
            pygame.draw.circle(cls._window, color, (x, y), radius)

    @classmethod
    def update_render_objects(cls) -> None:
        if storage.camera:
            new_render_objects_list = [obj for obj in cls.objects if obj._ignore_render_check or obj.rect.colliderect(storage.camera.render_zone)]
            
            for obj in storage.render_objects_list:
                if ( obj not in new_render_objects_list):
                    obj.on_exit_render_zone()
                    if obj.destroy_on_render_exit:
                        obj.destroy()

            storage.render_objects_list = new_render_objects_list

            CollisionSystem.update_visible_objects(storage.render_objects_list)

    @classmethod
    def debug_render(cls, window: pygame.Surface) -> None:
        ''' Отрисовка debug элементов. Скрыт если в настройка DEBUG == False '''
        camera = storage.camera
        pygame.draw.rect(window, (0, 0, 0), camera.deadzone, 1)

        text_surface = cls._debug_font.render(str(int(cls._current_fps)), False, (155, 0, 0))
        RenderSystem._window.blit(text_surface, (0, 0))
        
    @classmethod
    def render_background(cls):
        cls._window.fill((25, 150, 250))

    @classmethod
    def _render_image_batch(cls, commands) -> None:
        for surface, rect in commands:
            if surface.get_size() != rect.size:
                surface = pygame.transform.scale(surface, rect.size)
            cls._window.blit(surface, rect.topleft)

    @classmethod
    def render(cls, camera) -> None:
        cls.render_background()

        groups = {}
        layer_objects = sorted(storage.render_objects_list, key=lambda item: item.z_index)
        for element in layer_objects:
            if not element.display:
                continue
            object_to_render = element.prepare_to_render(camera)
            if not groups.get(object_to_render['type']):
                groups[object_to_render['type']] = []
            groups[object_to_render['type']].append(object_to_render['data'])

        for type in groups:
            if type == 'rect':
                cls._render_rect_batch(groups[type])
            elif type == 'circle':
                cls._render_circle_batch(groups[type])
            elif type == 'image':
                cls._render_image_batch(groups[type])

        if DEBUG:
            cls.debug_render(cls._window)

        pygame.display.update()

    @classmethod
    def on_change_objects_list(cls, action=None, item=None, *args, **kwargs) -> None:
        if item and not item._ignore_render_check:
            cls.update_render_objects()
            super().on_change_objects_list(action, item, *args, **kwargs)
        else:
            if action == 'append':
                storage.render_objects_list.append(item)

    @classmethod
    def update_before_render(cls):
        for obj in storage.render_objects_list:
            obj.update_before_render()

    @classmethod
    def update_after_render(cls) -> None:
        for obj in cls.objects:
            obj.update_after_render()

    @classmethod
    def update(cls) -> None:
        if not EventsSystem.is_frozen:
            cls.update_before_render()
            storage.camera.update(storage.camera.target or storage.player)
            cls.render(storage.camera)
            cls.update_after_render()
        else:
            cls.render(storage.camera)

    @classmethod
    def destroy(cls, item) -> None:
        res = super().destroy(item)
        if item in storage.render_objects_list:
            storage.render_objects_list.remove(item)
        return res
