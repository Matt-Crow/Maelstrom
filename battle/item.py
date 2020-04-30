from utilities import STATS, ELEMENTS
from stat_classes import *
import random

from output import Op
from upgradable import AbstractUpgradable

class ItemSet(object):
    """
    An item set is a
    combination of three
    items that will give
    the user a powerful
    bonus
    """
    def __init__(self, name, bonus_function):
        self.name = name
        self.f = bonus_function

    @staticmethod
    def get_set_bonus(set_name):
        def set_f(user):
            def f(event):
                Op.add("An error was encountered")
                Op.add("item set by name of")
                Op.add(set_name)
                Op.add("does not exist")
                Op.dp()
            user.add_on_update_action(set_f)
        ret = ItemSet("ERROR", set_f)
        for set in sets:
            if set.name == set_name:
                ret = set
        return ret.f
"""
Items need weather specific, stat codes
"""
class Item(AbstractUpgradable):
    types = {
        "ring": "We wants it.",
        "trinket": "Fresh from the street vendor.",
        "gem": "It holds a secret power.",
        "gear": "It comes from another dimension.",
        "greeble": "It looks incredible fun to play with."
    }
    def __init__(self, name: str):
        super(Item, self).__init__(name)
        self.set_type('Item')

        self.randomize_type()
        self.generate_random_enh()

        self.set_name = None
        self.equipped = False

        self.add_attr('boost', Stat('boost', boost_form, 0))
        self.track_attr('item_type')
        self.track_attr('desc')
        self.track_attr('set_name')
        self.track_attr('boosted_stat')


    def randomize_type(self):
        """
        Sets this to a random item type
        and sets its description appropriately
        Has no impact on this, just flavor
        """
        self.item_type = random.choice(list(Item.types.keys()))
        self.desc = Item.types[self.item_type]


    def generate_random_enh(self):
        """
        randomizes this' enhancement
        """
        enh_type = random.choice(("element+", "element-", "stat*"))
        if enh_type == "element+":
            boosted_element = random.choice(ELEMENTS)
            self.boosted_stat = boosted_element + ' damage multiplier'

        elif enh_type == "element-":
            boosted_element = random.choice(ELEMENTS)
            self.boosted_stat = boosted_element + ' damage reduction'

        else:
            self.boosted_stat = random.choice(STATS)


    def get_boost(self) -> 'Boost':
        """
        Returns the boost this will provide when equipped
        """
        return Boost(self.boosted_stat, self.get_stat('boost'), -1, self.name)


    def equip(self, user):
        self.user = user
        self.equipped = True

    def unequip(self):
        self.user = None
        self.equipped = False

    def apply_boosts(self):
        self.user.boost(self.get_boost())

    def getDisplayData(self):
        ret = [
            self.name + ":",
            "\t" + self.type
        ]
        for line in self.get_boost().getDisplayData():
            ret.append("\t" + line)
        ret.append("\t" + self.desc)
        return ret


    @staticmethod
    def read_json(json: dict) -> 'Item':
        """
        Reads a JSON object as a dictionary, then converts it to an Item
        """
        #some way to auto-do this?
        name = json.get("name", "NAME NOT FOUND")
        custom_points = int(json.get('customization_points', 0))

        ret = Item(name)
        ret.boosted_stat = json.get('boosted_stat', 'potency')
        ret.item_type = json.get('item_type', 'ITEM TYPE NOT FOUND')
        ret.desc = json.get('desc', 'DESCRIPTION NOT FOUND')
        ret.set_base('boost', int(json.get('boost', {'base': 0}).get('base', 0))) #since stat is stored in json now
        ret.set_name = json.get('set_name', None)
        ret.customization_points = custom_points
        return ret


    @staticmethod
    def get_defaults() -> list:
        """
        """
        i1 = Item.read_json({
        'name' : 'Item 1',
        'boost' : {
            'type': 'Stat',
            'base': 10,
            'name': 'boost'
        },
        'boosted_stat' : 'luck',
        'item_type' : 'TEST',
        'desc' : 'test item 1',
        'set_name' : 'Test item set'
        })

        return [i1]


def test_set_f(user):
    def f(event):
        Dp.add("Three piece bonus works!")
        Dp.dp()
    user.add_on_hit_taken_action(f)

sets = [
    ItemSet("Test item set", test_set_f)
]


def boost_form(base: int) -> float:
    """
    Calculate how much the should boost a stat by
    """
    return 0.1 + 0.025 * base


t1 = Item("Testitem 1")
t2 = Item("Testitem 2")
t3 = Item("Testitem 3")
