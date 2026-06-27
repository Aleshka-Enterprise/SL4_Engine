import pygame

from game.core.components.gameplay.event.event_mixin import EventMixin
from game.core.components.phisics.collision.collision_types import CollisionResponseTypes
from game.core.storage import storage
from game.core.components.phisics.collision import CollisionSystem
from game.settings import KEYS
from game.utils.types import Event, EventState


class DebugRender(EventMixin):
    COLLISION_COLORS = {
        CollisionResponseTypes.PUSH: (0, 255, 0),
        CollisionResponseTypes.IGNORE: (255, 255, 0),
        CollisionResponseTypes.STATIC: (255, 0, 0),
    }

    CAMERA_DEADZONE_ACTIVE_COLOR = (0, 255, 0)
    CAMERA_DEADZONE_DISABLED_COLOR = (200, 0, 0)
    FPS_COLOR = (155, 0, 0)
    INFO_COLOR = (200, 200, 200)

    def __init__(self):
        self.window = None
        self.debug_font = pygame.font.SysFont(None, 30)

        self.render_debug = True

        self.event_listener = [
            Event(KEYS.USE_DEBUG_RENDER, EventState.KEY_DOWN, self.__toggle_debug_render),
        ]
    
    def __toggle_debug_render(self):
        self.render_debug = not self.render_debug

    def render_camera_debug(self):
        camera = storage.camera

        if not camera:
            return

        deadzone_color = self.CAMERA_DEADZONE_ACTIVE_COLOR if camera.target else self.CAMERA_DEADZONE_DISABLED_COLOR

        cx = camera.deadzone.x + camera.deadzone.width // 2
        cy = camera.deadzone.y + camera.deadzone.height // 2
        pygame.draw.rect(self.window, deadzone_color, camera.deadzone, 2)
        pygame.draw.line(self.window, deadzone_color, (cx - 10, cy), (cx + 10, cy), 1)
        pygame.draw.line(self.window, deadzone_color, (cx, cy - 10), (cx, cy + 10), 1)

        if camera.target:
            player_screen = camera.apply((camera.target.x, camera.target.y))
            px, py = int(player_screen[0]), int(player_screen[1])
            pygame.draw.circle(self.window, (255, 0, 0), (px, py), 4)
            pygame.draw.line(self.window, (255, 255, 0), (cx, cy), (px, py), 1)

            if hasattr(camera, 'current_offset_x'):
                end_x = px + camera.current_offset_x
                end_y = py + camera.current_offset_y
                pygame.draw.line(self.window, (0, 255, 255), (px, py), (end_x, end_y), 2)
                pygame.draw.circle(self.window, (0, 255, 255), (int(end_x), int(end_y)), 3)

    def render_camera_info(self):
        ''' Отображаем инофрмацию из камеры текстом '''
        camera = storage.camera
        if not camera:
            return

        lines = [
            f"Viewport: ({int(camera.viewport.x)}, {int(camera.viewport.y)})",
            f"Offset X: {camera.current_offset_x:.1f}",
            f"Offset Y: {camera.current_offset_y:.1f}",
            f"Displayed objects: {len(storage.render_objects_list)}",
        ]

        if camera.target:
            lines.append(f"Camera target world: ({int(camera.target.x)}, {int(camera.target.y)})")
            ps = camera.apply((camera.target.x, camera.target.y))
            lines.append(f"Camera target screen: ({int(ps[0])}, {int(ps[1])})")

        # Рисуем текст, начиная с y=30 (чтобы не перекрывать FPS, который у вас в (0,0))
        y_offset = 30
        for line in lines:
            text_surface = self.debug_font.render(line, False, self.INFO_COLOR)
            self.window.blit(text_surface, (10, y_offset))
            y_offset += 25

    def render_fps(self):
        ''' Отображает текущий FPS '''
        fps = storage.clock.get_fps()
        text_surface = self.debug_font.render(str(int(fps)), False, self.FPS_COLOR)
        self.window.blit(text_surface, (0, 0))

    def render_collision_rects(self):
        ''' Отображает рамки коллизий всех объектов (или выбранных) для отладки '''
        visible_collision_object_list = CollisionSystem.visible_collision_object_list
        for obj in visible_collision_object_list:
            position = storage.camera.apply((obj.x, obj.y))
            color = self.COLLISION_COLORS.get(obj.collision_response, (0, 0, 0))

            pygame.draw.rect(self.window, color, [*position, obj.width, obj.height], 2)


    def render(self, window):
        self.window = window
        
        if self.render_debug:
            self.render_collision_rects()
            self.render_camera_debug()
            self.render_fps()
            self.render_camera_info()
