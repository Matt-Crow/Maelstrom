from utilities import *
from stat_classes import *

# TODO: add ability to customize side effects

"""
Actives:
"""
class AbstractActive(object):
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
    
    def add_side_effect(self, boost, chance = 100):
        """
        Add a boost to inflict upon hitting
        """
        self.side_effects.append({"effect": boost, "chance":chance}) 
    
    def set_user(self, user):
        self.user = user
        self.distribute_damage()
    
    def init_for_battle(self):
        self.distribute_damage()
        for side_effect in self.side_effects:
            side_effect["effect"].reset()
    
    def customize(self):
        """
        Start by showing what the attack's 
        stats are
        """
        self.init_for_battle()
        self.display_data()
        """        
        choice = choose("Do you want to change these damage stats, add a side effect, or change an existing one?", ("stats", "add effect", "change effect"))
        if choice == "stat":
            self.customize_damages()
        elif choice == "add effect":
            self.choose_effect_to_add()
        """
        self.customize_damages()
        # and display again
        self.init_for_battle()
        self.display_data()    
    
    def customize_damages(self):
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
        self.init_for_battle()
        Op.add(self.name)
        Op.indent()
        for type, value in self.damages.items():
            Op.add(type + " damage: " + str(int(value)))
        Op.unindent()
        Op.add("Critical hit chance: " + str(self.crit) + "%")
        Op.add("Miss chance: " + str(self.miss) + "%")
        Op.add("Critical hit multiplier: " + str(int(self.crit_mult * 100)) + "%")
        Op.add("Miss multiplier: " + str(int(self.miss_mult * 100)) + "%")
        Op.add("Cleave damage: " + str(int(self.cleave * 100)) + "% of damage from initial hit")
        #Op.add("SIDE EFFECTS:")
        Op.indent()
        for side_effect in self.side_effects:
            Op.add(str(side_effect["chance"]) + "% chance to inflict")
            side_effect["effect"].display_data()
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
    
    def generate_save_code(self):
        ret = ["<ACTIVE>: " + self.name]
        ret.append("*" + str(self.dmg_mult))
        ret.append(str(self.cleave) + "%")
        for k, v in self.damage_distribution.items():
            ret.append(k + ": " + str(v))
        ret.append("m%: " + str(self.miss))
        ret.append("c%: " + str(self.crit))
        ret.append("m*: " + str(self.miss_mult))
        ret.append("c*: " + str(self.crit_mult))
        ret.append("ENE: " + str(self.energy_cost))
        for status in self.side_effects:
            ret.append(status["effect"].generate_save_code() + ": " + str(status["chance"]) + "%")
        return ret
    
    @staticmethod
    def read_save_code(code):
        ret = None
        
        # start with the name
        name = ignore_text(code[0], "<ACTIVE>:").strip()
        dmg_mult = float(ignore_text(code[1], "*"))
        cleave = int(float(ignore_text(code[2], "%")) * 100)
        # * 100 is to counteract initializer
        new_dist = dict()
        for i in range(3, 8):
            line = code[i].split(":")
            new_dist[line[0].strip()] = int(float(line[1]))
        miss_c = int(float(ignore_text(code[8], "m%:")))
        crit_c = int(float(ignore_text(code[9], "c%:")))
        miss_m = float(ignore_text(code[10], "m*:"))
        crit_m = float(ignore_text(code[11], "c*:"))
        cost = int(float(ignore_text(code[12], "ENE: ")))
        
        #boosts...
        boosts = dict()
        boost_codes = code[13:]
        
        for boost_code in boost_codes:
            line = boost_code.split(":")
            boosts[Boost.read_save_code(line[0])] = int(float(ignore_text(line[1], "%")))
        
        if crit_c is not 0:
            ret = MeleeAttack(name, dmg_mult, miss_c, crit_c, miss_m, crit_m, cleave)
        
        else:
            ret = AbstractActive(name, dmg_mult, cleave, cost)
        
        ret.set_damage_distributions(new_dist)
        for boost, chance in boosts.items():
            ret.add_side_effect(boost, chance)
        
        return ret

class MeleeAttack(AbstractActive):
    def __init__(self, name, dmg, miss, crit, miss_mult, crit_mult, cleave):
        super(MeleeAttack, self).__init__(name, dmg, cleave, 0)
        self.miss = miss
        self.crit = crit
        self.miss_mult = miss_mult
        self.crit_mult = crit_mult