"""
Room

Rooms are simple containers that has no location of their own.

"""
from copy import deepcopy

from evennia import AttributeProperty, DefaultCharacter
from evennia.objects.objects import DefaultRoom
from evennia.utils import inherits_from
from random import choice, random
from evennia import TICKER_HANDLER

from .objects import ObjectParent


CHAR_SYMBOL = "|w@|n"
CHAR_ALT_SYMBOL = "|w>|n"
ROOM_SYMBOL = "|bo|n"
LINK_COLOR = "|B"

_MAP_GRID = [
    [" ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " "],
    [" ", " ", "@", " ", " "],
    [" ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " "],
]
_EXIT_GRID_SHIFT = {
    "north": (0, 1, "||"),
    "east": (1, 0, "-"),
    "south": (0, -1, "||"),
    "west": (-1, 0, "-"),
    "northeast": (1, 1, "/"),
    "southeast": (1, -1, "\\"),
    "southwest": (-1, -1, "/"),
    "northwest": (-1, 1, "\\"),
}




class Room(ObjectParent, DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Objects.
    """

    allow_combat = AttributeProperty(False, autocreate=False)
    allow_pvp = AttributeProperty(False, autocreate=False)
    allow_death = AttributeProperty(False, autocreate=False)

    def at_object_creation(self):
        self.db.is_dark = False

    def get_light(self):
        return self.db.is_dark

    def format_appearance(self, appearance, looker, **kwargs):
        """Don't left-strip the appearance string"""
        return appearance.rstrip()

    def get_display_header(self, looker, **kwargs):
        """
        Display the current location as a mini-map.

        """
        # make sure to not show make a map for users of screenreaders.
        # for optimization we also don't show it to npcs/mobs
        if not inherits_from(looker, DefaultCharacter) or (
                looker.account and looker.account.uses_screenreader()
        ):
            return ""

        # build a map
        map_grid = deepcopy(_MAP_GRID)
        dx0, dy0 = 2, 2
        map_grid[dy0][dx0] = CHAR_SYMBOL
        for exi in self.exits:
            dx, dy, symbol = _EXIT_GRID_SHIFT.get(exi.key, (None, None, None))
            if symbol is None:
                # we have a non-cardinal direction to go to - indicate this
                map_grid[dy0][dx0] = CHAR_ALT_SYMBOL
                continue
            map_grid[dy0 + dy][dx0 + dx] = f"{LINK_COLOR}{symbol}|n"
            if exi.destination != self:
                map_grid[dy0 + dy + dy][dx0 + dx + dx] = ROOM_SYMBOL

        # Note that on the grid, dy is really going *downwards* (origo is
        # in the top left), so we need to reverse the order at the end to mirror it
        # vertically and have it come out right.
        return "  " + "\n  ".join("".join(line) for line in reversed(map_grid))


class PvPRoom(Room):

    allow_combat = AttributeProperty(True, autocreate=False)
    allow_pvp = AttributeProperty(True, autocreate=False)

    def get_display_footer(self, looker, **kwargs):
        """
        Customize footer of description.
        """
        return "|yNon-lethal PvP combat is allowed here!|n"

class EchoingRoom(Room):
    """A room that randomly echoes messages to everyone inside it"""

    echoes = AttributeProperty(list, autocreate=False)
    echo_rate = AttributeProperty(60 * 2, autocreate=False)
    echo_chance = AttributeProperty(0.1, autocreate=False)

    def send_echo(self):
        if self.echoes and random() < self.echo_chance:
            self.msg_contents(choice(self.echoes))

    def start_echo(self):
        TICKER_HANDLER.add(self.echo_rate, self.send_echo)

    def stop_echo(self):
        TICKER_HANDLER.remove(self.echo_rate, self.send_echo)



