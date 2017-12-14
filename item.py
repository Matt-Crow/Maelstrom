from utilities import *
from stat_classes import *

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
    def __init__(self, name, type = None, enhancements = None, desc = None, set = None):
        self.name = name
        if type not in Item.types.keys():
            self.randomize_type()
        if desc == None:
            self.generate_desc()
        if enhancements == None:
            self.enhancements = []
            self.generate_random_enh()
        else:
            self.enhancements = to_list(enhancements)
        
        self.set = set
        self.equipped = False
    
    def randomize_type(self):
        self.type = random.choice(Item.types.keys())
    
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
    
    def display_data(self):
        Op.add(self.name + ":")
        Op.add(self.type)
        for enhancement in self.enhancements:
            Op.indent()
            enhancement.display_data()
        Op.unindent()
        Op.add(self.desc)
        Op.dp()

    def generate_save_code(self):
        ret = ["<ITEM>: " + self.name]
        ret.append("type: " + self.type)
        ret.append("desc: " + self.desc)
        ret.append("set: " + self.set.name)
        for enh in self.enhancements:
            ret.append(enh.generate_save_code())
        return ret

def test_set_f(user):
    def f(event):
        Dp.add("Three piece bonus works!")
        Dp.dp()
    user.add_on_hit_taken_action(f)
test_set = ItemSet("Test item set", test_set_f)

t1 = Item("Testitem 1", None, None, None, test_set)
t2 = Item("Testitem 2", None, None, None, test_set)
t3 = Item("Testitem 3", None, None, None, test_set)