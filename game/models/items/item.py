from game.core.components.render import RenderMixin
from game.core.storage import storage


class Item(RenderMixin):
    def __init__(self, is_pickable: bool = False, is_dropable: bool = False, **kwargs):
        super().__init__(**kwargs)
        
        self.is_pickable = is_pickable
        self.is_dropable = is_dropable
        self.z_index = 10
        
        storage.items.append(self)

    @property
    def item_type(self) -> str:
        return 'item'

    @property
    def can_pick(self):
        return self.is_pickable

    @property
    def can_drop(self):
        return self.is_dropable
