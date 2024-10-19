from evennia import create_object
from evennia.utils.test_resources import EvenniaTest

from typeclasses.npc import NPC


class Zombie(EvenniaTest):

    def test_npc_base(self):
        npc = create_object(
            NPC,
            key="TestNPC",
            attributes=[("hit_dice", 4)],  # set hit_dice to 4
        )

        self.assertEqual(npc.hp_multiplier, 4)
        self.assertEqual(npc.hp, 16)
        self.assertEqual(npc.strength, 4)
        self.assertEqual(npc.charisma, 4)