from utilities import *
from stat_classes import *

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
    def __init__(self, name, type = None, enhancements = None, desc = None):
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