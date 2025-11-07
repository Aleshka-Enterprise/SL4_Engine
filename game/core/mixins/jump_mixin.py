from game.core.mixins.base_mixin import BaseMixin

class JumpMixin(BaseMixin):
    def __init__(
        self,
        jump_force: int = -24,
        gravity: float = 1,
        on_the_ground: bool = False,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self._is_jumping = False
        self.vel_y = 0 # Вертикальная скорость
        self.gravity = gravity
        self.jump_force = jump_force
        self.on_the_ground = on_the_ground
        
    @property
    def is_jumping(self):
        return self._is_jumping
    
    @is_jumping.setter
    def is_jumping(self, value):
        if not self.can_jump() and value:
            return

        if self._is_jumping != value:
            if value:
                self.on_start_jump()
            else:
                self.on_end_jump()

        if not self._is_jumping:
            self._is_jumping = value
            if self._is_jumping:
                self.vel_y = self.jump_force
    
    def can_jump(self) -> bool:
        return self.on_the_ground

    def on_start_jump(self) -> None:
        pass
    
    def on_end_jump(self) -> None:
        pass
    
    def jump(self):
        self.is_jumping = True
    