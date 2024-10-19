"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter
from evennia.utils import lazy_property

from .equipment import EquipmentHandler, EquipmentError
from .objects import ObjectParent
from evennia import AttributeProperty, logger
from .rules import dice


class LivingMixin(AttributeProperty):
    # makes it easy for mobs to know to attack PCs
    is_pc = False

    @property
    def hurt_level(self):
        """
        String describing how hurt this character is.
        """
        percent = max(0, min(100, 100 * (self.hp / self.hp_max)))
        if 95 < percent <= 100:
            return "|gPerfect|n"
        elif 80 < percent <= 95:
            return "|gScraped|n"
        elif 60 < percent <= 80:
            return "|GBruised|n"
        elif 45 < percent <= 60:
            return "|yHurt|n"
        elif 30 < percent <= 45:
            return "|yWounded|n"
        elif 15 < percent <= 30:
            return "|rBadly wounded|n"
        elif 1 < percent <= 15:
            return "|rBarely hanging on|n"
        elif percent == 0:
            return "|RCollapsed!|n"


    def heal(self, hp):
        """
        Heal hp amount of health, not allowing to exceed our max hp

        """
        damage = self.hp_max - self.hp
        healed = min(damage, hp)
        self.hp += healed

        self.msg(f"You heal for {healed} HP.")


    def at_pay(self, amount):
        """When paying coins, make sure to never detract more than we have"""
        amount = min(amount, self.coins)
        self.coins -= amount
        return amount


    def at_attacked(self, attacker, **kwargs):
        """Called when being attacked and combat starts."""
        pass


    def at_damage(self, damage, attacker=None):
        """Called when attacked and taking damage."""
        self.hp -= damage


    def at_defeat(self):
        """Called when defeated. By default this means death."""
        self.at_death()


    def at_death(self):
        """Called when this thing dies."""
        # this will mean different things for different living things
        pass


    def at_do_loot(self, looted):
        """Called when looting another entity"""
        looted.at_looted(self)


    def at_looted(self, looter):
        """Called when looted by another entity"""

        # default to stealing some coins
        max_steal = dice.roll("1d10")
        stolen = self.at_pay(max_steal)
        looter.coins += stolen


class Character(ObjectParent, DefaultCharacter, LivingMixin):
    """
    The Character defaults to reimplementing some of base Object's hook methods with the
    following functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead).
    at_post_move(source_location) - Launches the "look" command after every move.
    at_post_unpuppet(account) -  when Account disconnects from the Character, we
                    store the current location in the prelogout_location Attribute and
                    move it to a None-location so the "unpuppeted" character
                    object does not need to stay on grid. Echoes "Account has disconnected"
                    to the room.
    at_pre_puppet - Just before Account re-connects, retrieves the character's
                    prelogout_location Attribute and move it back on the grid.
    at_post_puppet - Echoes "AccountName has entered the game" to the room.

    """

    is_pc = True

    strength = AttributeProperty(1)
    dexterity = AttributeProperty(1)
    constitution = AttributeProperty(1)
    intelligence = AttributeProperty(1)
    wisdom = AttributeProperty(1)
    charisma = AttributeProperty(1)
    luck = AttributeProperty(1)

    hp = AttributeProperty(8)
    hp_max = AttributeProperty(8)

    level = AttributeProperty(1)
    xp = AttributeProperty(0)
    coins = AttributeProperty(0)

    charclass = AttributeProperty("Fighter")
    charrace = AttributeProperty("Human")

    @lazy_property
    def equipment(self):
        return EquipmentHandler(self)

    def at_defeat(self):
        """Characters roll on the death table"""
        if self.location.allow_death:
            # this allow rooms to have non-lethal battles
            self.at_death()

        else:
            self.location.msg_contents(
                "$You() $conj(collapse) in a heap, alive but beaten.",
                from_obj=self)
            self.heal(self.hp_max)

    def at_death(self):
        """We rolled 'dead' on the death table."""
        self.location.msg_contents(
            "$You() collapse in a heap, embraced by death.",
            from_obj=self)
        # TODO - go back into chargen to make a new character!



    def at_pre_move(self, destination, **kwargs):
       """
       Called by self.move_to when trying to move somewhere. If this returns
       False, the move is immediately cancelled.
       """
       if self.db.is_sitting:
           self.msg("You need to stand up first.")
           return False
       return True

    def at_pre_object_receive(self, moved_object, source_location, **kwargs):
        """Called by Evennia before object arrives 'in' this character (that is,
        if they pick up something). If it returns False, move is aborted.

        """
        return self.equipment.validate_slot_usage(moved_object)

    def at_object_receive(self, moved_object, source_location, **kwargs):
        """
        Called by Evennia when an object arrives 'in' the character.

        """
        try:
            self.equipment.add(moved_object)
        except EquipmentError:
            logger.log_trace()

    def at_object_leave(self, moved_object, destination, **kwargs):
        """
        Called by Evennia when object leaves the Character.

        """
        self.equipment.remove(moved_object)



