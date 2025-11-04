from game.objects.shoot.poison.poison import Poison
from game.objects.items.weapons.weapon import Weapon
from random import randint


class PoisonGun(Weapon):
    def __init__(self, experation_time=1000, **kwargs):
        super().__init__(**kwargs)
        self.experation_time = experation_time
        self.no_ready_color = (0, 200, 0)

    def attack(self) -> bool:
        if self.can_atack():
            shoot = Poison(
                x=self.x + randint(0, 10),
                y=self.y + randint(-10, 10),
                direction=self.entity.direction,
                height=2,
                width=40,
                owner_weapon=self,
                damage=self.damage,
                initializer=self.entity,
                experation_time=200,
                color=(0, 100, 0),
                speed=50
                )

            self.shoot_list.append(shoot)

        return super().attack()
