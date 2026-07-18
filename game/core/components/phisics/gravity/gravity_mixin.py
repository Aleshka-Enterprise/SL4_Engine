from game.core.components.base.base_mixin import BaseMixin
from game.core.components.phisics.gravity.gravity_system import GravitySystem


class GravityMixin(BaseMixin):
    def __init__(self, vel_y: int = 900, gravity: int = 1800, **kwargs):
        super().__init__(**kwargs)

        self._vel_y = vel_y
        self._gravity = gravity
        self.is_on_ground = False

        if self.auto_register:
            GravitySystem.register(self)

    @property
    def vel_y(self):
        return self._vel_y

    @vel_y.setter
    def vel_y(self, value):
        self._vel_y = value

    @property
    def gravity(self):
        return self._gravity

    @gravity.setter
    def gravity(self, value):
        self._gravity = value

    def on_lend(self, platform: BaseMixin) -> None:
        """Слушатель события: объект приземлился"""
        pass

    def destroy(self) -> None:
        GravitySystem.destroy(self)
        return super().destroy()
