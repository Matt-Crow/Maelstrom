from utilities import *
from stat_classes import *
import random

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
class Item(object):
    types = {
        "ring": "We wants it.",
        "trinket": "Fresh from the street vendor.",
        "gem": "It holds a secret power.",
        "gear": "It comes from another dimension.",
        "greeble": "It looks incredible fun to play with."
    }
    def __init__(self, name, type = None, enhancements = None, desc = None, set_name = None):
        self.name = name
        if type not in Item.types.keys():
            self.randomize_type()
        else:
            self.type = type

        if desc == None:
            self.generate_desc()
        else:
            self.desc = desc

        if enhancements == None:
            self.enhancements = []
            self.generate_random_enh()
        else:
            self.enhancements = to_list(enhancements)

        self.set_name = set_name
        self.equipped = False

    def randomize_type(self):
        self.type = random.choice(list(Item.types.keys()))

    def generate_desc(self):
        self.desc = Item.types[self.type]

    def generate_random_enh(self):
        """
        Applies a random enhancement
        """
        enh_type = random.choice(("element+", "element-", "stat*"))
        if enh_type == "element+":
            boosted_element = random.choice(ELEMENTS)
            self.enhancements.append(Boost(boosted_element + " damage multiplier", 10, -1, self.name))
        elif enh_type == "element-":
            boosted_element = random.choice(ELEMENTS)
            self.enhancements.append(Boost(boosted_element + " damage reduction", 10, -1, self.name))
        else:
            boosted_stat = random.choice(STATS)
            self.enhancements.append(Boost(boosted_stat, 10, -1, self.name))

    def equip(self, user):
        self.user = user
        self.equipped = True

    def unequip(self):
        self.user = None
        self.equipped = False

    def apply_boosts(self):
        for enh in self.enhancements:
            self.user.boost(enh)

    def get_data(self):
        ret = [
            self.name + ":",
            "\t" + self.type
        ]
        for enhancement in self.enhancements:
            for line in enhancement.get_data():
                ret.append("\t" + line)
        ret.append("\t" + self.desc)
        return ret

    def __str__(self):
        return self.name

    def generate_save_code(self):
        ret = ["<ITEM>: " + self.name]
        ret.append("type: " + self.type)
        ret.append("desc: " + self.desc)
        ret.append("set: " + self.set_name)
        for enh in self.enhancements:
            ret.append(enh.generate_save_code())
        return ret

    @staticmethod
    def read_save_code(code):
        ret = None
        name = ignore_text(code[0], "<ITEM>:").strip()
        type = ignore_text(code[1], "type: ").strip()
        desc = ignore_text(code[2], "desc: ").strip()
        set = ignore_text(code[3], "set: ").strip()
        enh = []
        enh_codes = code[4:]
        for enh_code in enh_codes:
            enh.append(Boost.read_save_code(enh_code))
        ret = Item(name, type, enh, desc, set)
        return ret

def test_set_f(user):
    def f(event):
        Dp.add("Three piece bonus works!")
        Dp.dp()
    user.add_on_hit_taken_action(f)

#tuples with one item are converted to that one item
sets = (
    ItemSet("Test item set", test_set_f),
    ItemSet("noexist", test_set_f)
)

t1 = Item("Testitem 1", None, None, None, "Test item set")
t2 = Item("Testitem 2", None, None, None, "Test item set")
t3 = Item("Testitem 3", None, None, None, "Test item set")
