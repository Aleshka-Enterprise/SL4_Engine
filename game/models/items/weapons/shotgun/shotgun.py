from game.models.shoot.shoot import Shoot
from game.models.items.weapons.weapon import Weapon
from random import randint


class Shotgun(Weapon):
    def __init__(self, number_of_bullets=3, **kwargs):
        super().__init__(**kwargs)
        self.number_of_bullets = number_of_bullets

    def attack(self) -> None:
        if self.can_atack():
            for _ in range(self.number_of_bullets):
                shoot = Shoot(
                    x=self.x + (0 if self.direction == 'left' else self.width),
                    y=self.y + randint(-10, 10),
                    direction=self.direction,
                    height=3,
                    width=5,
                    owner_weapon=self,
                    damage=self.damage,
                    initializer=self.entity,
                    )

        return super().attack()
