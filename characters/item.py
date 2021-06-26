from utilities import STATS, ELEMENTS
from stat_classes import *
from util.output import Op
from customizable import AbstractCustomizable
import random

#          isn't really customizable
class Item(AbstractCustomizable):
    types = {
        "ring": "We wants it.",
        "trinket": "Fresh from the street vendor.",
        "gem": "It holds a secret power.",
        "gear": "It comes from another dimension.",
        "greeble": "It looks incredible fun to play with."
    }
    randomItemNumber = 0

    """
    kwargs:
    - name : str (defaults to random name)
    - itemType : str (default to a random type)
    - desc : str (defaults to the given itemType's description, or 'no description')
    - boostedStat : str (defaults to a random stat)
    """
    def __init__(self, **kwargs):
        super(Item, self).__init__(**dict(kwargs, name=Item.getItemName(kwargs), type="Item"))

        self.itemType = kwargs.get("itemType", random.choice(list(Item.types.keys())))
        self.desc = kwargs.get("desc", Item.types.get(self.itemType, "no description"))
        self.boostedStat = kwargs.get("boostedStat", random.choice(STATS))

        self.equipped = False

        self.addSerializedAttributes(
            "itemType",
            "desc",
            "boostedStat"
        )

    @staticmethod
    def getItemName(kwargs: dict)->str:
        ret = None
        if hasattr(kwargs, "name"):
            ret = kwargs["name"]
        else:
            ret = "Random Item #" + str(Item.randomItemNumber)
            Item.randomItemNumber += 1
        return ret

    """
    Reads a JSON object as a dictionary, then converts it to an Item
    """
    @classmethod
    def deserializeJson(cls, jdict: dict)->"Item":
        return Item(**jdict)

    @staticmethod
    def getDefaults() -> list:
        return [Item()]

    """
    Returns the boost this will provide when equipped
    """
    def getBoost(self) -> "Boost":
        #                              boosts by 10%
        return Boost(self.boostedStat, 0.1, -1, self.name)

    def equip(self, user):
        self.user = user
        self.equipped = True

    def unequip(self):
        self.user = None
        self.equipped = False

    def applyBoost(self):
        self.user.boost(self.getBoost())

    def getDisplayData(self):
        ret = [
            self.name + ":",
            "\t" + self.itemType
        ]
        for line in self.getBoost().getDisplayData():
            ret.append("\t" + line)
        ret.append("\t" + self.desc)
        return ret
