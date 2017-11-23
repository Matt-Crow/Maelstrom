from utilities import *

"""
Stat stuff
"""
class Stat(object):
    """
    A class used to store
    information about a stat,
    making it easier to keep 
    track of values
    """
    def __init__(self, name, base, enable_leveling = False):
        self.name = name
        self.base_value = float(base)
        self.boosts = []
        self.value = float(base)
        self.can_level_up = enable_leveling
    
    def calc(self, level):
        if not self.can_level_up:
            level = 0
        self.value = self.base_value * (1 + 0.2 * level)
    
    def boost(self, boost):
        self.boosts.append(boost)
    
    def get(self):
        mult = 1.0
        for boost in self.boosts:
            mult += boost.amount
        return self.value * mult
    
    def reset_boosts(self):
        self.boosts = []
    
    def update(self):
        new_boosts = []
        for boost in self.boosts:
            """
            a stat boost with a duration
            of 1 will be checked, then
            down to 0, while a duration
            of -1 will always fail the 
            check; thus, lasting forever
            """
            if boost.duration != 0:
                new_boosts.append(boost)
                boost.duration -= 1
        self.boosts = new_boosts
    
    def display_data(self):
        Dp.add(self.name);
        Dp.add("Raw: " + str(self.base_value))
        Dp.add("Boosts:")
        for boost in self.boosts:
            boost.display_data()
        Dp.add("Calculated: " + str(self.value))
        Dp.dp()

class Boost(object):
    def __init__(self, stat_name, amount, duration, id = "NoIDSet"):
        """
        stat should be a string
        """
        self.stat_name = stat_name
        self.amount = amount
        if abs(self.amount) > 1.0:
            self.amount = float(self.amount) / 100
        self.duration = duration
        self.id = id
    
    def display_data(self):
        Op.add("Boost: " + self.id)
        Op.add("+" + str(int(self.amount * 100)) + "% to")
        Op.add(self.stat_name + " stat")
        Op.add("for " + str(self.duration) + " turns")
        Op.dp()
    
    def generate_save_code(self):
        """
        Returns a string that is 
        used for save files        
        """
        ret = "b " + self.id + "/"
        ret += self.stat_name + "/"
        ret += str(self.amount) + "/"
        ret += str(self.duration)
        return ret