from game.core.components.render.text.text_mixin import TextMixin


class Text(TextMixin):
    def __init__(self, z_index=1000, **kwargs):
        super().__init__(**kwargs)

        self.z_index = z_index
