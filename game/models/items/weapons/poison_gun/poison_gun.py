import random

from game.models.items.weapons.weapon import Weapon
from game.models.shoot.poison.poison import Poison


class PoisonGun(Weapon):
    def __init__(self, experation_time=1000, **kwargs):
        super().__init__(**kwargs)
        self.experation_time = experation_time
        self.no_ready_color = "#00c800"

    def attack(self) -> bool:
        if self.can_atack():
            Poison(
                x=self.x + (-50 if self.direction == "left" else self.width),
                y=self.y + random.randint(-10, 10),
                direction=self.direction,
                height=2,
                width=40,
                owner_weapon=self,
                damage=self.damage,
                initializer=self.entity,
                experation_time=3,
                color="#006400",
                speed=1500,
            )

        return super().attack()
