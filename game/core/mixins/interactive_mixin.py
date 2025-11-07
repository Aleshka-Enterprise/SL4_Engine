from pygame import Rect
from game.core.storage import storage
from game.core.mixins.base_mixin import BaseMixin


class InteractiveMixin(BaseMixin):
    def __init__(self, intractive_width=100, interactive_height=100, **kwargs):
        super().__init__(**kwargs)
        self.__interactive_width = intractive_width
        self.__interactive_height = interactive_height
    
    @property
    def __interactive_zone_rect(self):
        return Rect(
            self.x - (self.__interactive_width / 2),
            self.y - (self.__interactive_height / 2),
            self.width + self.__interactive_width,
            self.height + self.__interactive_height
        )
    
    def update_interactive_zone(self, height: int, width: int) -> None:
        ''' Изменение зоны взаимодействия '''
        self.__interactive_height = height
        self.__interactive_width = width

    def take_item(self, type: str = None, ignore=[]) -> None:
        for item in (obj for obj in storage.render_objects_list if obj in storage.items and obj.can_pick):
            if (
                self.__interactive_zone_rect.colliderect(item.rect) and
                (not type or type == item.item_type) and
                not item in ignore
            ):
                return item