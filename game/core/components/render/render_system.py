import pygame
from game.core.components.base.base_system import BaseSystem
from game.core.components.render.debug_render import DebugRender
from game.core.components.render.render_types import RenderComand, RenderType
from game.settings import DISPLAY, DEBUG, WINDOW_CAPTION
from game.core.storage import storage
from game.core.components.phisics.collision import CollisionSystem
from game.core.components.gameplay.event import EventsSystem


class RenderSystem(BaseSystem):
    pygame.font.init()

    _debug_render = DebugRender()

    _window: pygame.Surface | None = None
    _sorted_cache = []           # кэш отсортированных объектов
    _cache_valid = False         # флаг "кэш актуален"

    is_freezable = False

    @classmethod
    def init_window(cls) -> pygame.Surface:
        '''Инициализация окна pygame'''
        if cls._window:
            return cls._window

        width = DISPLAY.WIDTH
        height = DISPLAY.HEIGHT
        window = pygame.display.set_mode((width, height), pygame.RESIZABLE, vsync=1)
        pygame.display.set_caption(WINDOW_CAPTION)
        cls._window = window
        return window
    
    @classmethod
    def invalidate_cache(cls):
        cls._cache_valid = False

    @classmethod
    def _get_sorted_objects(cls):
        if not cls._cache_valid:
            cls._sorted_cache = sorted(
                storage.render_objects_list,
                key=lambda item: item.z_index
            )
            cls._cache_valid = True
        return cls._sorted_cache

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
            cls.invalidate_cache()

            CollisionSystem.update_visible_objects(storage.render_objects_list)

    @classmethod
    def render(cls, camera) -> None:
        cls._window.fill((25, 150, 250))

        sorted_objects = cls._get_sorted_objects()
        viewport = camera.viewport
        
        for element in sorted_objects:
            if not element.display:
                continue
            if not element._ignore_render_check and not element.rect.colliderect(viewport):
                continue
            data_list: list[RenderComand] = element.prepare_to_render(camera)

            for comand in data_list:
                if comand.type == RenderType.RECT:
                    pygame.draw.rect(cls._window, **comand.data)
                elif comand.type == RenderType.CIRCLE:
                    pygame.draw.circle(cls._window, **comand.data)
                elif comand.type == RenderType.IMAGE:
                    surface, rect = comand.data['surface'], comand.data['rect']
                    cls._window.blit(surface, rect.topleft)
                elif comand.type == RenderType.TEXT:
                    surface, rect = comand.data['surface'], comand.data['rect']
                    cls._window.blit(surface, rect.topleft)
                elif DEBUG:
                    print(f"Unknown render type: {comand.type}")
        
        if DEBUG:
            cls._debug_render.render(cls._window)

        pygame.display.flip()

    @classmethod
    def on_change_objects_list(cls, action=None, item=None, *args, **kwargs) -> None:
        super().on_change_objects_list(action, item, *args, **kwargs)
        cls.invalidate_cache()

        if item and not item._ignore_render_check:
            cls.update_render_objects()
        else:
            if action == 'append':
                storage.render_objects_list.append(item)
            elif action == 'remove':
                if item in storage.render_objects_list:
                    storage.render_objects_list.remove(item)
            elif action == 'clear':
                storage.render_objects_list.clear()

    @classmethod
    def update_before_render(cls, dt):
        for obj in storage.render_objects_list:
            obj.update_before_render(dt)

    @classmethod
    def update_after_render(cls, dt) -> None:
        for obj in cls.objects:
            obj.update_after_render(dt)

    @classmethod
    def update(cls, dt: float = 1.0) -> None:
        if not EventsSystem.is_frozen:
            cls.update_before_render(dt)
            storage.camera.update(dt)
            cls.render(storage.camera)
            cls.update_after_render(dt)
        else:
            cls.render(storage.camera)

    @classmethod
    def destroy(cls, item) -> None:
        res = super().destroy(item)
        if item in storage.render_objects_list:
            storage.render_objects_list.remove(item)
            cls.invalidate_cache()
        return res
