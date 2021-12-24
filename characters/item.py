from utilities import STATS
from stat_classes import *
from customizable import AbstractCustomizable
from util.stringUtil import entab
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
    - name : str
    - itemType : str (default to a random type)
    - desc : str (defaults to the given itemType's description, or 'no description')
    - boostedStat : str (defaults to a random stat)
    """
    def __init__(self, **kwargs):
        super(Item, self).__init__(**dict(kwargs, name=kwargs["name"], type="Item"))

        self.itemType = kwargs.get("itemType", random.choice(list(Item.types.keys())))
        self.desc = kwargs.get("desc", Item.types.get(self.itemType, "no description"))
        self.boostedStat = kwargs.get("boostedStat", random.choice(STATS))

        self.equipped = False

        self.addSerializedAttributes(
            "itemType",
            "desc",
            "boostedStat"
        )

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

    def getDisplayData(self)->str:
        ret = [
            f'{self.name}: {self.itemType}',
            entab(self.getBoost().getDisplayData()),
            entab(f'"{self.desc}"')
        ]
        return "\n".join(ret)
