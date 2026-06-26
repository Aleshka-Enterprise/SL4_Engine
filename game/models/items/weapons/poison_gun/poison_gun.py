import random

from game.models.shoot.poison.poison import Poison
from game.models.items.weapons.weapon import Weapon


class PoisonGun(Weapon):
    def __init__(self, experation_time=1000, **kwargs):
        super().__init__(**kwargs)
        self.experation_time = experation_time
        self.no_ready_color = (0, 200, 0)

    def attack(self) -> bool:
        if self.can_atack():
            shoot = Poison(
                x=self.x + (-50 if self.direction == 'left' else self.width),
                y=self.y + random.randint(-10, 10),
                direction=self.direction,
                height=2,
                width=40,
                owner_weapon=self,
                damage=self.damage,
                initializer=self.entity,
                experation_time=200,
                color=(0, 100, 0),
                speed=50
                )

        return super().attack()
