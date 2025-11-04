from game.objects.shoot.shoot import Shoot
from game.objects.items.weapons.weapon import Weapon
from random import randint


class Shotgun(Weapon):
    def __init__(self, number_of_bullets=3, **kwargs):
        super().__init__(**kwargs)
        self.number_of_bullets = number_of_bullets

    def attack(self) -> None:
        if self.can_atack():
            for _ in range(self.number_of_bullets):
                shoot = Shoot(
                    x=self.x + randint(-10, 10),
                    y=self.y + randint(-10, 10),
                    direction=self.entity.direction,
                    height=3,
                    width=5,
                    owner_weapon=self,
                    damage=self.damage,
                    initializer=self.entity
                    )
                self.shoot_list.append(shoot)

        return super().attack()
