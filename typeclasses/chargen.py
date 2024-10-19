from evennia import create_object, spawn, EvMenu

from .characters import Character
from .random_tables import chargen_tables
from .rules import dice


_TEMP_SHEET = """
{name}

STR +{strength}
DEX +{dexterity}
CON +{constitution}
INT +{intelligence}
WIS +{wisdom}
CHA +{charisma}
LCK +{luck}

{description}

Your belongings:
{equipment}
"""


class TemporaryCharacterSheet:

    def _random_ability(self):
        return min(dice.roll("1d6"), dice.roll("1d6"), dice.roll("1d6"))

    def __init__(self):
        self.ability_changes = 0  # how many times we tried swap abilities

        # name will likely be modified later
        self.name = dice.roll_random_table("1d282", chargen_tables["name"])

        # base attribute values
        self.strength = self._random_ability()
        self.dexterity = self._random_ability()
        self.constitution = self._random_ability()
        self.intelligence = self._random_ability()
        self.wisdom = self._random_ability()
        self.charisma = self._random_ability()
        self.luck = self._random_ability()

        # physical attributes (only for rp purposes)
        physique = dice.roll_random_table("1d20", chargen_tables["physique"])

        self.desc = (
            f"You are {physique}"
        )

        #
        self.hp_max = max(5, dice.roll("1d8"))
        self.hp = self.hp_max
        self.xp = 0
        self.level = 1

        # random equipment
        self.armor = "Pechera de cuero"

        self.helmet = "helmet"
        self.shield = "shield"

        self.weapon = "Espada"

        self.backpack = [
            "ration",
            "ration",
        ]

    def show_sheet(self):
        equipment = (
            str(item)
            for item in [self.armor, self.helmet, self.shield, self.weapon] + self.backpack
            if item
        )

        return _TEMP_SHEET.format(
            name=self.name,
            strength=self.strength,
            dexterity=self.dexterity,
            constitution=self.constitution,
            intelligence=self.intelligence,
            wisdom=self.wisdom,
            charisma=self.charisma,
            luck=self.luck,
            description=self.desc,
            equipment=", ".join(equipment),
        )

    def apply(self):
        # create character object with given abilities
        new_character = create_object(
            Character,
            key=self.name,
            attrs=(
                ("strength", self.strength),
                ("dexterity", self.dexterity),
                ("constitution", self.constitution),
                ("intelligence", self.intelligence),
                ("wisdom", self.wisdom),
                ("charisma", self.wisdom),
                ("luck", self.luck),
                ("hp", self.hp),
                ("hp_max", self.hp_max),
                ("desc", self.desc),
            ),
        )
        # spawn equipment (will require prototypes created before it works)
        if self.weapon:
            weapon = spawn(self.weapon)
            new_character.equipment.move(weapon)
        if self.shield:
            shield = spawn(self.shield)
            new_character.equipment.move(shield)
        if self.armor:
            armor = spawn(self.armor)
            new_character.equipment.move(armor)
        if self.helmet:
            helmet = spawn(self.helmet)
            new_character.equipment.move(helmet)

        for item in self.backpack:
            item = spawn(item)
            new_character.equipment.store(item)

        return new_character


def node_chargen(caller, raw_string, **kwargs):

    tmp_character = kwargs["tmp_character"]

    text = tmp_character.show_sheet()

    options = [
        {
            "desc": "Change your name",
            "goto": ("node_change_name", kwargs)
        }
    ]
    if tmp_character.ability_changes <= 0:
        options.append(
            {
                "desc": "Swap two of your ability scores (once)",
                "goto": ("node_swap_abilities", kwargs),
            }
        )
    options.append(
        {
            "desc": "Accept and create character",
            "goto": ("node_apply_character", kwargs)
        },
    )

    return text, options


def _update_name(caller, raw_string, **kwargs):
    """
    Used by node_change_name below to check what user
    entered and update the name if appropriate.

    """
    if raw_string:
        tmp_character = kwargs["tmp_character"]
        tmp_character.name = raw_string.lower().capitalize()

    return "node_chargen", kwargs


def node_change_name(caller, raw_string, **kwargs):
    """
    Change the random name of the character.

    """
    tmp_character = kwargs["tmp_character"]

    text = (
        f"Your current name is |w{tmp_character.name}|n. "
        "Enter a new name or leave empty to abort."
    )

    options = {
        "key": "_default",
        "goto": (_update_name, kwargs)
    }

    return text, options

_ABILITIES = {
    "STR": "strength",
    "DEX": "dexterity",
    "CON": "constitution",
    "INT": "intelligence",
    "WIS": "wisdom",
    "CHA": "charisma",
    "LCK": "luck",
}


def _swap_abilities(caller, raw_string, **kwargs):
    """
    Used by node_swap_abilities to parse the user's input and swap ability
    values.

    """
    if raw_string:
        abi1, *abi2 = raw_string.split(" ", 1)
        if not abi2:
            caller.msg("That doesn't look right.")
            return None, kwargs
        abi2 = abi2[0]
        abi1, abi2 = abi1.upper().strip(), abi2.upper().strip()
        if abi1 not in _ABILITIES or abi2 not in _ABILITIES:
            caller.msg("Not a familiar set of abilites.")
            return None, kwargs

        # looks okay = swap values. We need to convert STR to strength etc
        tmp_character = kwargs["tmp_character"]
        abi1 = _ABILITIES[abi1]
        abi2 = _ABILITIES[abi2]
        abival1 = getattr(tmp_character, abi1)
        abival2 = getattr(tmp_character, abi2)

        setattr(tmp_character, abi1, abival2)
        setattr(tmp_character, abi2, abival1)

        tmp_character.ability_changes += 1

    return "node_chargen", kwargs


def node_swap_abilities(caller, raw_string, **kwargs):
    """
    One is allowed to swap the values of two abilities around, once.

    """
    tmp_character = kwargs["tmp_character"]

    text = f"""
        Your current abilities:
        
        STR +{tmp_character.strength}
        DEX +{tmp_character.dexterity}
        CON +{tmp_character.constitution}
        INT +{tmp_character.intelligence}
        WIS +{tmp_character.wisdom}
        CHA +{tmp_character.charisma}
        LCK +{tmp_character.luck}
        
        You can swap the values of two abilities around.
        You can only do this once, so choose carefully!
        
        To swap the values of e.g.  STR and INT, write |wSTR INT|n. Empty to abort.
        """

    options = {"key": "_default", "goto": (_swap_abilities, kwargs)}

    return text, options


def node_apply_character(caller, raw_string, **kwargs):
    """
    End chargen and create the character. We will also puppet it.

    """
    tmp_character = kwargs["tmp_character"]
    new_character = tmp_character.apply(caller)
    caller.characters.add(new_character)

    text = "Character created!"

    return text, None


def start_chargen(caller, session=None):
    """
    This is a start point for spinning up the chargen from a command later.

    """

    menutree = {
        "node_chargen": node_chargen,
        "node_change_name": node_change_name,
        "node_swap_abilities": node_swap_abilities,
        "node_apply_character": node_apply_character,
    }

    # this generates all random components of the character
    tmp_character = TemporaryCharacterSheet()

    EvMenu(
        caller,
        menutree,
        startnode="node_chargen",
        session=session,
        startnode_input=("", {"tmp_character": tmp_character}),
    )