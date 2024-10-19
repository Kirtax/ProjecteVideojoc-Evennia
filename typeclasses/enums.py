from enum import Enum

class Ability(Enum):
    """
    The six base ability-bonuses and other
    abilities

    """

    STR = "strength"
    DEX = "dexterity"
    CON = "constitution"
    INT = "intelligence"
    WIS = "wisdom"
    CHA = "charisma"
    LCK = "luck"

    ARMOR = "armor"

    CRITICAL_SUCCESS = "critical_success"

    ALLEGIANCE_HOSTILE = "hostile"
    ALLEGIANCE_NEUTRAL = "neutral"
    ALLEGIANCE_FRIENDLY = "friendly"


ABILITY_REVERSE_MAP =  {
    "str": Ability.STR,
    "dex": Ability.DEX,
    "con": Ability.CON,
    "int": Ability.INT,
    "wis": Ability.WIS,
    "cha": Ability.CHA,
    "lck": Ability.LCK
}


class WieldLocation(Enum):
    BACKPACK = "backpack"
    MAIN_HAND = "main_hand"
    OFF_HAND = "off_hand"
    TWO_HANDS = "two_handed_weapons"
    BODY = "body"  # armor
    HEAD = "head"  # helmets


class ObjType(Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    SHIELD = "shield"
    HELMET = "helmet"
    CONSUMABLE = "consumable"
    GEAR = "gear"
    MAGIC = "magic"
    QUEST = "quest"
    TREASURE = "treasure"