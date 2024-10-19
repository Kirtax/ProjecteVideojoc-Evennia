from random import randint
from .enums import Ability

class RollEngine:

    def roll(self, roll_string):
        """
        Roll XdY dice, where X is the number of dice
        and Y the number of sides per die.

        Args:
            roll_string (str): A dice string on the form XdY.
        Returns:
            int: The result of the roll.

        """

        # split the XdY input on the 'd' one time
        number, diesize = roll_string.split("d", 1)

        # convert from string to integers
        number = int(number)
        diesize = int(diesize)

        # make the roll
        return sum(randint(1, diesize) for _ in range(number))

    def roll_with_advantage_or_disadvantage(self, advantage=False, disadvantage=False):

        if not (advantage or disadvantage) or (advantage and disadvantage):
            # normal roll - advantage/disadvantage not set or they cancel
            # each other out
            return self.roll("1d100")
        elif advantage:
            # highest of two d100 rolls
            return max(self.roll("1d100"), self.roll("1d100"))
        else:
            # disadvantage - lowest of two d100 rolls
            return min(self.roll("1d100"), self.roll("1d100"))

    def saving_throw(self, character, bonus_type, target, advantage=False, disadvantage=False):
        """
        Do a saving throw, trying to beat a target.

        Args:
           character (Character): A character (assumed to have Ability bonuses
               stored on itself as Attributes).
           bonus_type (Ability): A valid Ability bonus enum.
           target (int): The target number to beat.
           advantage (bool): If character has advantage on this roll.
           disadvantage (bool): If character has disadvantage on this roll.

        Returns:
            tuple: A tuple (bool, Ability), showing if the throw succeeded and
                the quality is one of None or Ability.CRITICAL_SUCCESS

        """

        # make a roll
        dice_roll = self.roll_with_advantage_or_disadvantage(advantage, disadvantage)

        # calculate luck modifier for potential critical success
        dice_roll_crit = randint(1, 50)
        luck_modifier = getattr(character, Ability.LCK.value, 1)

        dice_roll_crit += luck_modifier

        # determine if it's a critical success
        quality = Ability.CRITICAL_SUCCESS if dice_roll_crit > target else None

        # figure out bonus
        bonus = getattr(character, bonus_type.value, 1)

        # return a tuple (bool, quality)
        return (dice_roll + bonus) > target, bonus

    def opposed_saving_throw(self, attacker, defender,
                             attack_type, defense_type=Ability.ARMOR,
                             advantage=False, disadvantage=False):

        defender_defense = getattr(defender, defense_type.value, 1)

        result, quality = self.saving_throw(attacker, bonus_type=attack_type,
                                            target=defender_defense,
                                            advantage=advantage, disadvantage=disadvantage)

        return result, quality

    def morale_check(self, defender):
        return self.roll("2d6") <= getattr(defender, "morale", 9)

    def roll_random_table(self, dieroll, table_choices):
        """
        Args:
             dieroll (str): A die roll string, like "1d20".
             table_choices (iterable): A list of either single elements or
                of tuples.
        Returns:
            Any: A random result from the given list of choices.

        Raises:
            RuntimeError: If rolling dice giving results outside the table.

        """
        roll_result = self.roll(dieroll)

        if isinstance(table_choices[0], (tuple, list)):
            # the first element is a tuple/list; treat as on the form [("1-5", "item"),...]
            for (valrange, choice) in table_choices:
                minval, *maxval = valrange.split("-", 1)
                minval = abs(int(minval))
                maxval = abs(int(maxval[0]) if maxval else minval)

                if minval <= roll_result <= maxval:
                    return choice

                    # if we get here we must have set a dieroll producing a value
            # outside of the table boundaries - raise error
            raise RuntimeError("roll_random_table: Invalid die roll")
        else:
            # a simple regular list
            roll_result = max(1, min(len(table_choices), roll_result))
            return table_choices[roll_result - 1]

class DamageEngine:
    def damage(self, damage_range):
        """
        Calculate damage based on the given damage range.

        Args:
            damage_range (str): A string representing the damage range in the format "min-max".

        Returns:
            int: A random number between the minimum and maximum values of the damage range.
        """
        # Parse the damage range
        min_damage, max_damage = map(int, damage_range.split('-'))

        # Calculate and return random damage within the range
        return randint(min_damage, max_damage)


dice = RollEngine()
damage_engine = DamageEngine()