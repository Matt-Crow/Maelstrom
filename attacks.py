from utilities import *

"""
Actives:
"""
class Active(object):
    """
    The attacks all characters can use
    """
    def __init__(self, name, mult, cleave_perc, energy_cost):
        """
        """
        self.name = name
        self.dmg_mult = mult
        
        self.damages = {}
        self.damage_distribution = {"physical":50}
        for element in ELEMENTS:
            self.damage_distribution[element] = 12.5
        
        self.cleave = float(cleave_perc) / 100
        
        self.miss = 0
        self.crit = 0
        self.miss_mult = 1.0
        self.crit_mult = 1.0
        self.energy_cost = energy_cost
        
        self.side_effects = []
    
    def set_damage_distributions(self, new_dist):
        """
        new_dist should be a dictionary
        """
        self.damage_distribution = new_dist
    
    def add_side_effect(self, function, chance = 100):
        self.side_effects.push({"effect": function, "chance":chance}) 
    
    def set_user(self, user):
        self.user = user
        self.distribute_damage()
    
    def init_for_battle(self):
        self.distribute_damage()
    
    def customize(self):
        """
        Start by showing what the attack's 
        stats are
        """
        self.distribute_damage()
        self.display_data()
        
        # copy the old attack data into new data
        new_data = {}
        for k, v in self.damage_distribution.items():
            new_data[k] = v
        
        can_down = []
        # make sure it would not be decreased past 0 
        #(base 12.5 system, can't be between 0 and 12.5)
        for k, v in self.damage_distribution.items():
            if v > 0:
                can_down.append(k)
        
        new_data[choose("Which damage stat do you want to increase by 12.5% of total damage?", new_data.keys())] += 12.5
        new_data[choose("Which damage stat do you want to decrease by 12.5%? of total damage", can_down)] -= 12.5
        self.set_damage_distributions(new_data)
        # and display again
        self.distribute_damage()
        self.display_data()    
    
    def distribute_damage(self):
        total = get_hit_perc(self.user.level) * self.dmg_mult
        split_between = 0
        self.damages = {}
        for value in self.damage_distribution.values():
            split_between += value
        for type, value in self.damage_distribution.items():
            self.damages[type] = total / split_between * value
    
    def total_dmg(self):
        ret = 0
        for damage in self.damages.values():
            ret += damage
        return ret
    
    def display_data(self):
        Op.add(self.name)
        for type, value in self.damages.items():
            Op.add(type + " damage: " + str(int(value)))
        Op.add("Critical hit chance: " + str(self.crit) + "%")
        Op.add("Miss chance: " + str(self.miss) + "%")
        Op.add("Critical hit multiplier: " + str(int(self.crit_mult * 100)) + "%")
        Op.add("Miss multiplier: " + str(int(self.miss_mult * 100)) + "%")
        Op.add("Cleave damage: " + str(int(self.cleave * 100)) + "% of damage from initial hit")
        Op.dp()
    
    def can_use(self):
        return self.user.energy >= self.energy_cost

    def calc_MHC(self):
        """
        Used to calculate hit type
        """
        ret = 1.0
	
        if (self.miss > 0 and self.crit > 0):
            rand = roll_perc(self.user.get_stat("luck"))
            Dp.add(["rand in calc_MHC: " + str(rand), "Crit: " + str(100 - self.crit), "Miss: " + str(self.miss)])
            Dp.dp()
            if rand <= self.miss:
                Op.add("A glancing blow!")
                ret = self.miss_mult
            
            elif rand >= 100 - self.crit:
                Op.add("A critical hit!")
                ret = self.crit_mult
            
        return ret
    
    def apply_side_effects_to(self, target):
        for side_effect in self.side_effects:
            rand = roll_perc(self.user.get_stat("luck"))
            
            Dp.add("Rolling for side effect...")
            Dp.add("Rolled: " + str(rand))
            Dp.add("Minimum to activate: " + str(side_effect["chance"]))
            Dp.dp()
            
            if rand > 100 - side_effect["chance"]:
                side_effect["effect"]()
            
    def use(self):
        self.user.lose_energy(self.energy_cost)
        if self.dmg_mult is not 0:
            self.user.team.enemy.active.take_DMG(self.user, self)
            self.apply_side_effects_to(self.user.team.enemy.active)
        if self.cleave is not 0:
            for enemy in self.user.team.enemy.members_rem:
                if enemy is not self.user.team.enemy.active:
                    enemy.direct_dmg(self.total_dmg() * self.cleave)
                    self.apply_side_effects_to(enemy)

class MeleeAttack(Active):
    def __init__(self, name, dmg, miss, crit, miss_mult, crit_mult, cleave):
        super(MeleeAttack, self).__init__(name, dmg, cleave, 0)
        self.miss = miss
        self.crit = crit
        self.miss_mult = miss_mult
        self.crit_mult = crit_mult