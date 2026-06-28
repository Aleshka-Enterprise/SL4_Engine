from game.core.components.phisics.gravity.gravity_mixin import GravityMixin

class JumpMixin(GravityMixin):
    def __init__(
        self,
        jump_force: int = -24,
        on_the_ground: bool = False,
        max_jump_count: int = 0,
        **kwargs
    ):
        super().__init__(**kwargs)

        self._is_jumping = False
        self.jump_force = jump_force
        self._on_the_ground = on_the_ground
        self.max_jump_count = max_jump_count
        self.current_jump_count = max_jump_count

    @property
    def on_the_ground(self):
        return self._on_the_ground
    
    @on_the_ground.setter
    def on_the_ground(self, value: bool):
        if value:
            self.current_jump_count = 0
        self._on_the_ground = value

    @property
    def is_jumping(self):
        return self._is_jumping

    @is_jumping.setter
    def is_jumping(self, value):
        if not self.can_jump() and value:
            return
        
        if value:
            self.vel_y = self.jump_force
            self.on_start_jump()
            self.current_jump_count += 1

        if self._is_jumping != value and not value:
            self.on_end_jump()

        if not self._is_jumping:
            self._is_jumping = value
            if self._is_jumping:
                self.vel_y = self.jump_force

    def can_jump(self) -> bool:
        ''' Проверка, можно ли совершить сейчас прыжок '''
        return (self.max_jump_count and self.max_jump_count > self.current_jump_count) or self.on_the_ground

    def on_start_jump(self) -> None:
        ''' Обработчик событий: начало прыжка '''
        pass

    def on_end_jump(self) -> None:
        ''' Обработчик события: конец прыжка '''
        pass

    def jump(self, dt=None) -> None:
        ''' Прыжок '''
        self.is_jumping = True
