from evennia import DefaultCharacter, AttributeProperty, create_object
from .objects import _BARE_HANDS
from .characters import LivingMixin
from .enums import Ability


class NPC(LivingMixin, DefaultCharacter):
    """Base class for NPCs"""

    is_pc = False
    hit_dice = AttributeProperty(default=1, autocreate=False)
    armor = AttributeProperty(default=1, autocreate=False)  # +10 to get armor defense
    hp_multiplier = AttributeProperty(default=4, autocreate=False)  # 4 default in Knave
    hp = AttributeProperty(default=None, autocreate=False)  # internal tracking, use .hp property
    morale = AttributeProperty(default=9, autocreate=False)
    allegiance = AttributeProperty(default=Ability.ALLEGIANCE_HOSTILE, autocreate=False)

    weapon = AttributeProperty(default=_BARE_HANDS, autocreate=False)  # instead of inventory
    coins = AttributeProperty(default=1, autocreate=False)  # coin loot

    is_idle = AttributeProperty(default=False, autocreate=False)


    @property
    def strength(self):
        return self.hit_dice


    @property
    def dexterity(self):
        return self.hit_dice


    @property
    def constitution(self):
        return self.hit_dice


    @property
    def intelligence(self):
        return self.hit_dice


    @property
    def wisdom(self):
        return self.hit_dice


    @property
    def charisma(self):
        return self.hit_dice


    @property
    def hp_max(self):
        return self.hit_dice * self.hp_multiplier


    def at_object_creation(self):
        """
        Start with max health.

        """
        self.hp = self.hp_max
        self.tags.add("npcs", category="group")


class Mob(NPC):
    """
    Mob(ile) NPC to be used for enemies.

    """

