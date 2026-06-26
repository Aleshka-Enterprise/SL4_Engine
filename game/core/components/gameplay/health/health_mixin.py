from game.core.components.base.base_mixin import BaseMixin


class HealthMixin(BaseMixin):
    def __init__(
        self,
        hp: int = 1,
        maximum: int = None,
        invulnerable: bool = False,
        destroy_after_dead: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)
        self._hp = hp
        self._max_hp = maximum or hp
        self.invulnerable = invulnerable
        self.destroy_after_dead = destroy_after_dead

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = min(value, self.max_hp)

        if self.hp <= 0:
            if self.invulnerable:
                self._hp = 1
            else:
                self.died()

    @property
    def max_hp(self) -> int:
        return self._max_hp

    def on_take_damage(self):
        ''' Слушатель события: получение урона '''
        pass

    def on_died(self):
        ''' Слушатель события: объект умер '''
        pass

    def died(self):
        ''' Смерть объекта. Вызывается если hp <= 0 '''
        self.on_died()

    def take_damage(self, damage) -> None:
        ''' Получить урон '''
        self.hp -= damage
        self.on_take_damage()
