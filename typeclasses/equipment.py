from evennia.utils import inherits_from

from .enums import WieldLocation, Ability
from .objects import ObjectParent, get_bare_hands


class EquipmentError(TypeError):
    """All types of equipment-errors"""
    pass

class EquipmentHandler:
    save_attribute = "inventory_slots"

    def __init__(self, obj):
        # here obj is the character we store the handler on
        self.obj = obj
        self._load()

    def _load(self):
        """Load our data from an Attribute on `self.obj`"""
        self.slots = self.obj.attributes.get(
            self.save_attribute,
            category="inventory",
            default={
                WieldLocation.MAIN_HAND: None,
                WieldLocation.OFF_HAND: None,
                WieldLocation.TWO_HANDS: None,
                WieldLocation.BODY: None,
                WieldLocation.HEAD: None,
                WieldLocation.BACKPACK: []
            }
        )

    def _save(self):
        """Save our data back to the same Attribute"""
        self.obj.attributes.add(self.save_attribute, self.slots, category="inventory")

    @property
    def max_slots(self):
        """Max amount of slots, based on CON defense (CON + 10)"""
        return getattr(self.obj, Ability.CON.value, 1) + 20

    def count_slots(self):
        """Count current slot usage"""
        slots = self.slots
        wield_usage = sum(
            getattr(slotobj, "size", 0) or 0
            for slot, slotobj in slots.items()
            if slot is not WieldLocation.BACKPACK
        )
        backpack_usage = sum(
            getattr(slotobj, "size", 0) or 0 for slotobj in slots[WieldLocation.BACKPACK]
        )
        return wield_usage + backpack_usage

    def get_current_slot(self, obj):
        """
        Check which slot-type the given object is in.

        Args:
            obj (EvAdventureObject): The object to check.

        Returns:
            WieldLocation: A location the object is in. None if the object
            is not in the inventory at all.

        """
        for equipment_item, slot in self.all():
            if obj == equipment_item:
                return slot

    def validate_slot_usage(self, obj):
        """
        Check if obj can fit in equipment, based on its size.

        """
        if not inherits_from(obj, ObjectParent):
            # in case we mix with non-evadventure objects
            raise EquipmentError(f"{obj.key} is not something that can be equipped.")

        size = obj.size
        max_slots = self.max_slots
        current_slot_usage = self.count_slots()
        return current_slot_usage + size <= max_slots

    def add(self, obj):
        """
        Put something in the backpack.
        """
        if self.validate_slot_usage(obj):
            self.slots[WieldLocation.BACKPACK].append(obj)
            self._save()

    def remove(self, obj_or_slot):
        """
        Remove specific object or objects from a slot.

        Returns a list of 0, 1 or more objects removed from inventory.
        """
        slots = self.slots
        ret = []
        if isinstance(obj_or_slot, WieldLocation):
            # a slot; if this fails, obj_or_slot must be obj
            if obj_or_slot is WieldLocation.BACKPACK:
                # empty entire backpack
                ret.extend(slots[obj_or_slot])
                slots[obj_or_slot] = []
            else:
                ret.append(slots[obj_or_slot])
                slots[obj_or_slot] = None
        elif obj_or_slot in self.slots.values():
            # obj in use/wear slot
            for slot, objslot in slots.items():
                if objslot is obj_or_slot:
                    slots[slot] = None
                    ret.append(objslot)
        elif obj_or_slot in slots[WieldLocation.BACKPACK]:             # obj in backpack slot
            try:
                slots[WieldLocation.BACKPACK].remove(obj_or_slot)
                ret.append(obj_or_slot)
            except ValueError:
                pass
        if ret:
            self._save()
        return ret

    def move(self, obj):
        """Move object from backpack to its intended `inventory_use_slot`."""

        # make sure to remove from equipment/backpack first, to avoid double-adding

        self.remove(obj)
        if not self.validate_slot_usage(obj):
            return

        slots = self.slots
        use_slot = getattr(obj, "inventory_use_slot", WieldLocation.BACKPACK)

        to_backpack = []
        if use_slot is WieldLocation.TWO_HANDS:
            # two-handed weapons can't co-exist with weapon/shield-hand used items
            to_backpack = [slots[WieldLocation.MAIN_HAND], slots[WieldLocation.OFF_HAND]]
            slots[WieldLocation.MAIN_HAND] = slots[WieldLocation.OFF_HAND] = None
            slots[use_slot] = obj
        elif use_slot in (WieldLocation.MAIN_HAND, WieldLocation.OFF_HAND):
            # can't keep a two-handed weapon if adding a one-handed weapon or shield
            to_backpack = [slots[WieldLocation.TWO_HANDS]]
            slots[WieldLocation.TWO_HANDS] = None
            slots[use_slot] = obj
        elif use_slot is WieldLocation.BACKPACK:
            # it belongs in backpack, so goes back to it
            to_backpack = [obj]
        else:
            # for others (body, head), just replace whatever's there
            replaced = [obj]
            slots[use_slot] = obj

        for to_backpack_obj in to_backpack:
            # put stuff in backpack
            slots[use_slot].append(to_backpack_obj)

        # store new state
        self._save()

    @property
    def armor(self):
        slots = self.slots
        return sum(
            (
                # armor is listed using its defense, so we remove 10 from it
                # (11 is base no-armor value in Knave)
                getattr(slots[WieldLocation.BODY], "armor", 1),
                # shields and helmets are listed by their bonus to armor
                getattr(slots[WieldLocation.MAIN_HAND], "armor", 0),
                getattr(slots[WieldLocation.OFF_HAND], "armor", 0),
                getattr(slots[WieldLocation.HEAD], "armor", 0),
            )
        )

    @property
    def weapon(self):
        # first checks two-handed wield, then one-handed; the two
        # should never appear simultaneously anyhow (checked in `move` method).
        slots = self.slots
        weapon = slots[WieldLocation.TWO_HANDS]
        if not weapon:
            weapon = slots[WieldLocation.MAIN_HAND]
        # if we still don't have a weapon, we return None here
        if not weapon:
            weapon = get_bare_hands()
        return weapon

    def display_loadout(self):
        """
        Get a visual representation of your current loadout.

        Returns:
            str: The current loadout.

        """
        slots = self.slots
        weapon_str = "You are fighting with your bare fists"
        shield_str = " and have no shield."
        armor_str = "You wear no armor"
        helmet_str = " and no helmet."

        two_hands = slots[WieldLocation.TWO_HANDS]
        if two_hands:
            weapon_str = f"You wield {two_hands} with both hands"
            shield_str = " (you can't hold a shield at the same time)."
        else:
            one_hands = slots[WieldLocation.MAIN_HAND]
            if one_hands:
                weapon_str = f"You are wielding {one_hands} in one hand."
            shield = slots[WieldLocation.OFF_HAND]
            if shield:
                shield_str = f"You have {shield} in your off hand."

        armor = slots[WieldLocation.BODY]
        if armor:
            armor_str = f"You are wearing {armor}"

        helmet = slots[WieldLocation.BODY]
        if helmet:
            helmet_str = f" and {helmet} on your head."

        return f"{weapon_str}{shield_str}\n{armor_str}{helmet_str}"

    def display_backpack(self):
        """
        Get a visual representation of the backpack's contents.

        """
        backpack = self.slots[WieldLocation.BACKPACK]
        if not backpack:
            return "Backpack is empty."
        out = []
        for item in backpack:
            out.append(f"{item.key} [|b{item.size}|n] slot(s)")
        return "\n".join(out)

    def display_slot_usage(self):
        """
        Get a slot usage/max string for display.

        Returns:
            str: The usage string.

        """
        return f"|b{self.count_slots()}/{self.max_slots}|n"

    def get_wieldable_objects_from_backpack(self):
        """
        Get all wieldable weapons (or spell runes) from backpack. This is useful in order to
        have a list to select from when swapping your wielded loadout.

        Returns:
            list: A list of objects with a suitable `inventory_use_slot`. We don't check
            quality, so this may include broken items (we may want to visually show them
            in the list after all).

        """
        return [
            obj
            for obj in self.slots[WieldLocation.BACKPACK]
            if obj
            and obj.id
            and obj.inventory_use_slot
            in (WieldLocation.MAIN_HAND, WieldLocation.TWO_HANDS, WieldLocation.OFF_HAND)
        ]

    def get_wearable_objects_from_backpack(self):
        """
        Get all wearable items (armor or helmets) from backpack. This is useful in order to
        have a list to select from when swapping your worn loadout.

        Returns:
            list: A list of objects with a suitable `inventory_use_slot`. We don't check
            quality, so this may include broken items (we may want to visually show them
            in the list after all).

        """
        return [
            obj
            for obj in self.slots[WieldLocation.BACKPACK]
            if obj and obj.id and obj.inventory_use_slot in (WieldLocation.BODY, WieldLocation.HEAD)
        ]

    def get_usable_objects_from_backpack(self):
        """
        Get all 'usable' items (like potions) from backpack. This is useful for getting a
        list to select from.

        Returns:
            list: A list of objects that are usable.

        """
        character = self.obj
        return [
            obj for obj in self.slots[WieldLocation.BACKPACK] if obj and obj.at_pre_use(character)
        ]

    def all(self):
        """
        Get all objects in inventory, regardless of location.
        """
        slots = self.slots
        lst = [
            (slots[WieldLocation.MAIN_HAND], WieldLocation.MAIN_HAND),
            (slots[WieldLocation.OFF_HAND], WieldLocation.OFF_HAND),
            (slots[WieldLocation.TWO_HANDS], WieldLocation.TWO_HANDS),
            (slots[WieldLocation.BODY], WieldLocation.BODY),
            (slots[WieldLocation.HEAD], WieldLocation.HEAD),
        ] + [(item, WieldLocation.BACKPACK) for item in slots[WieldLocation.BACKPACK]]
        return lst


