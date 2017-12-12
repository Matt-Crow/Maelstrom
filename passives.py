from utilities import *
from stat_classes import *

"""
needs work
"""

"""
Passives
"""
# work on negative boosts
class AbstractPassive(object):
    """
    HOW TO ADD A PASSIVE TO A CHARACTER:
    1. define the passive:
    * pas = ~~~Passive(~ ~ ~ ~ ~ ~)
    2. append the passive:
    * character.passives.append(pas)
    3. set the user:
    * pas.set_user(character)
    """
    def __init__(self, name, boosts):
        self.name = name
        self.boosts = to_list(boosts)
    
    def set_user(self, user):
        self.user = user
    
    def f(self):
        for boost in self.boosts:
            # if it's possitive, affect the user
            if boost.amount > 0:
                self.user.boost(boost)
            else:
                self.user.team.enemy.active.boost(boost)
    
    def display_data(self):
        Op.add("TODO: " + self.name + " display_data")
        Op.dp()

class Threshhold(AbstractPassive):
    """
    Automatically invoked at the end of every turn
    """
    def __init__(self, name, threshhold, boosts):
        super(self.__class__, self).__init__(name, boosts)
        self.threshhold = threshhold
    
    def init_for_battle(self):
        self.user.add_on_update_action(self.check_trigger)
    
    def check_trigger(self):
        Dp.add("Checking trigger for " + self.name)
        Dp.add(str(self.threshhold) + "% threshhold")
        Dp.add(str(self.user.hp_perc()) + "% user health")
        if self.user.hp_perc() <= self.threshhold:
            Dp.add("activated")
            self.f()
        Dp.dp()
    
    # add checks for all boosts undurationed
    def customize(self):
        self.display_data()
        options = ["Potency", "Duration"]
        if self.threshhold <= 95:
            options.append("Threshhold")
        
        choice = choose("What do you want to improve?", options)
        
        if choice == "Threshhold":
            self.threshhold += 5
        elif choice == "Potency":
            for boost in self.boosts:
                boost.amount += 0.05
        else:
            for boost in self.boosts:
                boost.base_duration += 1 
        
        options = []
        if self.threshhold > 5:
            options.append("Threshhold")
        can_pot = True
        can_dur = True
        
        for boost in self.boosts:
            if abs(boost.amount) <= 5:
                can_pot = False
            if boost.base_duration <= 1:
                can_dur = False
        if can_pot:
            options.append("Potency")
        if can_dur:
            options.append("Duration")
        
        choice = choose("Which stat do you want to decrease?", options)
        if choice == "Threshhold":
            self.threshhold -= 5
        elif choice == "Potency":
            for boost in self.boosts:
                boost.amount -= 0.05
        else:
            for boost in self.boosts:
                boost.base_duration -= 1
        
        self.display_data()
    
    def display_data(self):
        Op.add(self.name + ":")
        Op.add("Inflicts user with:")
        for boost in self.boosts:
            Op.indent()
            boost.display_data()
        Op.add("when at or below")
        Op.add(str(self.threshhold) + "% maximum Hit Points") 
        Op.dp()
    
    def generate_save_code(self):
        """
        Returns a sequence used 
        to save data across multiple
        play sessions with help from
        save file
        """
        ret = ["p " + self.name]
        ret.append("thresh: " + str(self.threshhold))
        for boost in self.boosts:
            ret.append(boost.generate_save_code())
        return ret 


class OnHitGiven(AbstractPassive):
    def __init__(self, name, chance, boosts):
        super(self.__class__, self).__init__(name, boosts)
        self.chance = chance
    
    def init_for_battle(self):
        self.user.add_on_hit_given_action(self.check_trigger)
    
    def check_trigger(self, onHitEvent):
        rand = roll_perc(self.user.get_stat("luck"))
        Dp.add("Checking trigger for " + self.name)
        Dp.add("Need to roll " + str(100 - self.chance) + " or higher to activate")
        Dp.add("Rolled " + str(rand))
        if rand > 100 - self.chance:
            Dp.add("activated")
            self.f()
        Dp.dp()
    
    def customize(self):
        self.display_data()
        
        options = ["Chance", "Potency", "Duration"]
        
        choice = choose("Which stat do you want to increase?", options)
        
        if choice == "Chance":
            self.chance += 5
        elif choice == "Potency":
            self.boost_amount += 5
        else:
            self.boost_duration += 1 
        
        
        choice = choose("Which stat do you want to decrease?", options)
        if choice == "Chance":
            self.chance += 5
        elif choice == "Potency":
            self.boost_amount -= 5
        else:
            self.boost_duration -= 1
        
        self.update_desc()
        self.display_data()
    
    def display_data(self):
        Op.add(self.name + ":")
        Op.add("Whenever the user strikes an opponent, ")
        Op.add("there is a " + str(self.chance) + "% chance that the")
        for boost in self.boosts:
            if boost.amount > 0:
                Op.add("user")
            else:
                Op.add("target")
            Op.add("will be inflicted with:")
            Op.indent()
            boost.display_data()
    
    def generate_save_code(self):
        """
        Returns a sequence used 
        to save data across multiple
        play sessions with help from
        save file
        """
        ret = ["p " + self.name]
        ret.append("given: " + str(self.chance))
        for boost in self.boosts:
            ret.append(boost.generate_save_code())
        return ret
    
class OnHitTaken(AbstractPassive):
    def __init__(self, name, chance, boosts):
        super(self.__class__, self).__init__(name, boosts)
        self.chance = chance
    
    def init_for_battle(self):
        self.user.add_on_hit_taken_action(self.check_trigger)
    
    def check_trigger(self, onHitEvent):
        rand = roll_perc(self.user.get_stat("luck"))
        Dp.add("Checking trigger for " + self.name)
        Dp.add("Need to roll " + str(100 - self.chance) + " or higher to activate")
        Dp.add("Rolled " + str(rand))
        if rand > 100 - self.chance:
            Dp.add("activated")
            self.f()
        Dp.dp()

    def customize(self):
        self.display_data()
        
        options = ["Chance", "Potency", "Duration"]
        
        choice = choose("Which stat do you want to increase?", options)
        
        if choice == "Chance":
            self.chance += 5
        elif choice == "Potency":
            self.boost_amount += 5
        else:
            self.boost_duration += 1 
        
        
        choice = choose("Which stat do you want to decrease?", options)
        if choice == "Chance":
            self.chance += 5
        elif choice == "Potency":
            self.boost_amount -= 5
        else:
            self.boost_duration -= 1
        
        self.update_desc()
        self.display_data()
    
    def display_data(self):
        Op.add(self.name + ":")
        Op.add("Whenever the user is struck by an opponent, ")
        Op.add("there is a " + str(self.chance) + "% chance that the")
        for boost in self.boosts:
            if boost.amount > 0:
                Op.add("user")
            else:
                Op.add("attacker")
            Op.add("will be inflicted with:")
            Op.indent()
            boost.display_data()
    
    def generate_save_code(self):
        """
        Returns a sequence used 
        to save data across multiple
        play sessions with help from
        save file
        """
        ret = ["p " + self.name]
        ret.append("taken: " + str(self.chance))
        for boost in self.boosts:
            ret.append(boost.generate_save_code())
        return ret