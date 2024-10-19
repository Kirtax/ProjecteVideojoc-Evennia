from typeclasses.objects import Object

class Monster(Object):
    """
    This is a base class for Monsters.
    """
    def move_around(self):
        print(f"{self.key} is moving!")


class Dragon(Monster):
    """
    This is a dragon-specific Monster.
    """

    def move_around(self):
        super().move_around()
        print("The world trembles.")

    def firebreath(self):
        """
        Let our dragon breathe fire.
        """
        print(f"{self.key} breathes fire!")