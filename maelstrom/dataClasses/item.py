"""
Items provide passive effects to characters upon whom they are equipped, much
like passive abilities. However, Items are easier to swap around than passives,
and can be acquired as rewards from Battles.
"""

from maelstrom.dataClasses.stat_classes import Boost
from maelstrom.gameplay.events import HIT_TAKEN_EVENT

class Item:

    def __init__(self, name, description, register):
        """
        name should be a unique identifier.
        register is a function that accepts an Character, and is called
        on this item's wielder at the start of an Encounter
        """
        self.name = name
        self.description = description
        self.register = register
        self.equipped = False

    def copy(self)->"Item":
        return Item(self.name, self.description, self.register)

    def setEquipped(self, equipped: bool):
        self.equipped = equipped

    def isEquipped(self)->bool:
        return self.equipped

    def registerTo(self, user):
        """
        applies this Item's bonus to the given user.

        This is not the same as calling setEquipped
        """
        self.register(user)

    def __str__(self):
        return f'Item {self.name}: "{self.description}"'



def getItemList():
    return [
        Item(
            "Rock",
            "I got a rock...",
            lambda character: character.boost(Boost("resistance", 0.1, -1, "Rock"))
        ),

        Item(
            "Copper Sword",
            "Strikes both in melee and like lightning",
            boostBothOffense
        ),

        Item(
            "Durasteel Armor",
            "Probably not great at blocking lightning",
            lambda character: character.add_event_listener(HIT_TAKEN_EVENT, lambda event: event.hitee.heal(event.damage / 4))
        )
    ]

def boostBothOffense(character):
    character.boost(Boost("control", 0.2, -1, "Copper Sword 1"))
    character.boost(Boost("energy", 0.2, -1, "Copper Sword 2"))
