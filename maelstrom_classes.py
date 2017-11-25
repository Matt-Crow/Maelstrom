if __name__ == "__main__":
    print("Oops! You're running from the wrong file!")
    print("Try running Maelstrom.py instead!")
    exit()

import random # still needed for non-luck things
from passives import *
from stat_classes import *

characters = {}
enemies = {}
passives = []
ELEMENTS = ("lightning", "rain", "hail", "wind")
STATS = ("control", "resistance", "potency", "luck", "energy")


def get_hit_perc(lv):
    """
    Calculates how much
    damage an attack should
    do to a target at a given
    level
    """
    return 16.67 * (1 + lv * 0.05)

def load():
    ret = Team("Test team", ({"name": "Alexandre", "level": 1}, 
    {"name": "Rene", "level": 1}, 
    {"name": "Ian", "level": 1}, 
    {"name": "Viktor", "level": 1}), 
    False)
    
    should_load = choose("Do you want to load from a save file?", ("Yes", "No"))
    
    if should_load == "Yes":
        file = Savefile("player_data.txt")
        ret = file.upload_team()
        
    return ret

# need to comment this
# ARRRGGG work here
class Savefile(object):
    def __init__(self, file):
        self.file = file
    
    def text_to_dict(self):
        self.dict_file = {}
        file_read = open(self.file, "r")
        for line in file_read:
            if line == " ":
                continue
            line = line.split("!")
            Dp.add(["Line.split:", line])
            for item in line:
                data = item.split()
                Dp.add(["Data.split:", data])
                if data[0] == "P":
                    for i in data:
                        if i == "P":
                            continue
                        else:
                            self.dict_file[name]["Passives"].append(i.replace("_", " "))
                else:
                    name = data[0]
                    self.dict_file[name] = {"Stats": [], "Passives": []}
            	    self.dict_file[name]["Stats"] = [data[1], data[2], data[3], data[4]]
        Dp.add(["Dict file:", self.dict_file])
        Dp.dp()
    
    def upload_team(self):
        self.text_to_dict()
        members = []
        for name, data in self.dict_file.items():
            Dp.add(["Name:", name, "Data:", data])
            members.append({"name": name, "level": int(data["Stats"][0])})
        Dp.add(["Members:", members])
        ret = Team("Player Team", members, False)
        Dp.dp()
        
        for member in ret.team:
            for name, data in self.dict_file.items():
                if member.name == name:
                    member.level_set = int(data["Stats"][1])
                    member.XP = int(data["Stats"][2])
                    member.stars = int(data["Stats"][3])
                    for passive in data["Passives"]:
                        member.add_passive(passive)
        return ret
    
    def update(self, team):
        self.text_to_dict()
        Dp.add(["Before:", self.dict_file])
        
        change = {}
        for member in team.team:
            change[member.name] = {"Stats": []}
            change[member.name]["Stats"] = [str(member.level), str(member.level_set), str(member.XP), str(member.stars)]
        self.dict_file = change
        Dp.add(["After:", self.dict_file])
        Dp.dp()
        file = open("player_data.txt", "w")
        new = " "
        for member, data in change.items():
            new = new + member + " "
            new = new + data["Stats"][0] + " "
            new = new + data["Stats"][1] + " "
            new = new + data["Stats"][2] + " "
            new = new + data["Stats"][3] + " "
            
        file.write(new)
        file.close()


"""
Events
"""
class AbstractEvent(object):
    def __init__(self, id):
        self.id = id
        
    def check_trigger(self):
        pass
        
    def trip(self):
        pass

class OnHitEvent(AbstractEvent):
    """
    an OnHitEvent is created during 
    battle whenever one character 
    hits another. The event is then
    passed in to all of the hitter's
    onHitGiven functions and all of
    the hitee's onHitTaken functions
    """
    def __init__(self, id, hitter, hitee, hit_by, damage):
        self.id = id
        self.hitter = hitter
        self.hitee = hitee
        self.hit_by = hit_by
        self.damage = damage
        
    def display_data(self):
        Dp.add("OnHitEvent " + self.id)
        Dp.add(self.hitter.name + " struck " + self.hitee.name)
        Dp.add("using " + self.hit_by.name)
        Dp.add("dealing " + str(self.damage) + " damage")
        Dp.dp()

"""
Actives:
"""
class AbstractAttack(object):
    """
    The attacks all characters can use
    """
    def __init__(self, name, mult, energy_cost):
        """
        """
        self.name = name
        self.dmg_mult = mult
        
        self.damages = {}
        self.damage_distribution = {"physical":50}
        for element in ELEMENTS:
            self.damage_distribution[element] = 12.5
        
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
    
    def display_data(self):
        Op.add(self.name)
        for type, value in self.damages.items():
            Op.add(type + " damage: " + str(int(value)))
        Op.add("Critical hit chance: " + str(self.crit) + "%")
        Op.add("Miss chance: " + str(self.miss) + "%")
        Op.add("Critical hit multiplier: " + str(int(self.crit_mult * 100)) + "%")
        Op.add("Miss penalty: " + str(int(self.miss_mult * 100)) + "%")
        Op.dp(False)
    
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
    
    def hit(self, target):
        target.take_DMG(self.user, self)
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

class ActAttack(AbstractAttack):
    def use(self):
        self.hit(self.user.team.enemy.active)
        super(ActAttack, self).use()

class MeleeAttack(ActAttack):
    def __init__(self, name, dmg, miss, crit, miss_mult, crit_mult):
        super(MeleeAttack, self).__init__(name, dmg, 0)
        self.miss = miss
        self.crit = crit
        self.miss_mult = miss_mult
        self.crit_mult = crit_mult

class AllAttack(AbstractAttack):
    def use(self):
        for member in self.user.team.enemy.members_rem:
            self.hit(member)
        super(type(self), self).use()

class AnyAttack(AbstractAttack):
    def use(self):    
        if self.user.team.AI:
            highest = 0
            best = None
            options = []
            if self.user.team.switched_in:
                m = 0.75
            else:
                m = 1.0
            
            for member in self.user.team.enemy.members_rem:
                damage = member.calc_DMG(self.user, self) * m
                if damage >= member.HP_rem:
                    options.append(member)
                if damage >= highest:
                    highest = damage
                    best = member
            
            if len(options) >= 1:
                target_team.members_rem[random.randint(0, len(options) - 1)].take_DMG(self.user, self)
            else:
                self.hit(best)
        else:
            self.hit(choose("Who do you wish to hit?", target_team.members_rem))
        super(type(self), self).use()

"""
Items need random generation, stat codes
"""
class Item(object):
    def __init__(self, name, type = "Greeble", enhancements = None, desc = None):
        self.name = name
        if desc == None:
            self.generate_desc(type)
        self.enhancements = to_list(enhancements)
        self.equipped = False
    
    def generate_desc(self, type):
        self.desc = "Do this later"
        
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
        for enhancement in self.enhancements:
            enhancement.display_data()
        Op.add(self.desc)

"""
Characters
"""
class AbstractCharacter(object):
    """
    A Class containing all the info for a character
    """
    
    """
    Initializers:
    Used to 'build' the characters
    """
    def __init__(self, name, data, level):
        """
        """
        self.name = name
        self.stats = [Stat("HP", 100)]
        
        self.set_stat_bases(data[0])
            
        self.stats.append(Stat("Physical damage multiplier", 100))
        
        self.stats.append(Stat("Physical damage reduction", 100))
        
        for element in ELEMENTS:
            self.stats.append(Stat(element + " damage multiplier", 100))
            self.stats.append(Stat(element + " damage reduction", 100))
        
        self.element = data[1]
        self.level = level
        self.XP = 0
        self.level_set = 1
        
        self.attacks = [data[2]]
        self.add_default_actives()
        self.set_passives_to_defaults()
        
        self.equipped_items = []
    
    def set_stat_bases(self, bases):
        """
        Set the base stat shifts
        """
        # we'll go through 5 stats
        stat_num = 0
        while stat_num < 5:
            val = Stat(STATS[stat_num], 20 + set_in_bounds(bases[stat_num], -5, 5), True)
            # check all of my existing stats...
            found = False
            search_num = 0
            while search_num < len(self.stats) and not found:
                # to see if the stat I'm asigning already exists
                if self.stats[search_num].name == STATS[stat_num]:
                    found = True
                    self.stats[search_num] = val
                search_num += 1
            if not found:
                self.stats.append(val)
            stat_num += 1
        self.stat_bases = bases
    
    #temporary
    def add_default_actives(self):
        self.attacks.append(MeleeAttack("slash", 1.0, 15, 15, 0.75, 1.5))
        self.attacks.append(MeleeAttack("jab", 0.75, 10, 40, 0.5, 2.0))
        self.attacks.append(MeleeAttack("slam", 1.35, 30, 15, 0.5, 1.35))
        for attack in self.attacks:
            attack.set_user(self)
    
    #temporary
    def set_passives_to_defaults(self):
        self.passives = []
        
        p = Threshhold("Threshhold test", 25, Boost("resistance", 20, 1, "Threshhold test"))
        self.passives.append(p)
        p.set_user(self)
        
        o = OnHitGiven("OnHitGivenTest", 25, Boost("luck", 20, 5, "OnHitGivenTest"))
        self.passives.append(o)
        o.set_user(self)
        
        h = OnHitTaken("OnHitTakenTest", 25, Boost("control", -20, 1, "OnHitTakenTest"), False)
        self.passives.append(h)
        h.set_user(self)
    
    def calc_stats(self):
        """
        Calculate a character's stats
        """
        for stat in self.stats:
            stat.calc(self.level)
    
    # HP defined here
    def init_for_battle(self):
        """
        Prepare for battle!
        """
        self.reset_action_registers()
        
        for stat in self.stats:
            stat.reset_boosts()
        for attack in self.attacks:
            attack.init_for_battle()
        for passive in self.passives:
            passive.init_for_battle()
        for item in self.equipped_items:
            item.apply_boosts()
        
        self.calc_stats()
        self.HP_rem = self.get_stat("HP")
        self.energy = int(self.get_stat("energy") / 2.0)
    
    # action register class?
    def reset_action_registers(self):
        """
        Action registers are used to
        hold functions which should be
        invoked whenever a specific
        condition is met, such as being
        hit. They should each take an 
        extendtion of AbstractEvent as
        a paramter
        """
        self.on_hit_given_actions = []
        self.on_hit_taken_actions = []
        self.on_update_actions = []
    
    def add_on_hit_given_action(self, action, duration = -1):
        """
        duration is how long to check for the condition
        """
        self.on_hit_given_actions.append({"function":action, "duration":duration})
    
    def add_on_hit_taken_action(self, action, duration = -1):
        """
        duration of -1 means it lasts forever in battle
        """
        self.on_hit_taken_actions.append({"function":action, "duration":duration})
    
    def add_on_update_action(self, action, duration = -1):
        """
        """
        self.on_update_actions.append({"function":action, "duration":duration})
    
    def update_action_registers(self):
        """
        Standard decrement, check, reasign
        pattern I use all the time
        """
        def update(register):
            new = []
            for action in register:
                action["duration"] -= 1
                # don't check if negative,
                # that way I can make stuff last forever
                if action["duration"] != 0:
                    new.append(action)
        update(self.on_hit_given_actions)
        update(self.on_hit_taken_actions)
        update(self.on_update_actions)
    
    """
    Data obtaining functions:
    Used to get data about a character
    """
    
    def hp_perc(self):
        """
        Returns as a value between 0 and 100
        """
        return int((float(self.HP_rem) / float(self.get_stat("HP"))) * 100.0)
    
    def get_stat(self, name):
        """
        Returns the calculated
        value of a given stat.
        If it is not found,
        notify Dp, and return -1
        """
        ret = -1
        for stat in self.stats:
            if stat.name.upper() == name.upper():
                ret = stat.get()
        
        if ret == -1:
            Dp.add("Stat not found: " + name)
            Dp.dp()
        
        return ret
    
    def get_stat_data(self, name):
        """
        Returns the stat object which
        matches name
        """
        ret = Stat("ERROR", 0)
        for stat in self.stats:
            if stat.name.upper() == name.upper():
                ret = stat
        
        if ret.name == "ERROR":
            Dp.add("Stat not found: " + name)
            Dp.dp()
        
        return ret
    
    def display_data(self):
        """
        Print info on a character
        """
        self.calc_stats()
        Op.add("Lv. " + str(self.level) + " " + self.name)
        Op.add(self.element)
        
        Op.add("STATS:")
        for stat in STATS:
            Op.add(stat + ": " + str(int(self.get_stat(stat))))
        
        Op.add("ACTIVES:")
        for attack in self.attacks:
            Op.add("-" + attack.name)
        
        Op.add("PASSIVES:")
        for passive in self.passives:
            Op.add("-" + passive.name)
        
        Op.add("ITEMS:")
        for item in self.equipped_items:
            Op.add("-" + item.name)
        
        Op.add(str(self.XP) + "/" + str(self.level * 10))
        Op.dp()
    
    def display_mutable_stats(self):
        for stat_name in STATS:
            Op.add(stat_name + ": " + str(int(self.get_stat(stat_name))))
        Op.dp(False)
    
    def display_items(self):
        for item in self.equipped_items:
            item.display_data()
    
    """
    Battle functions:
    Used during battle
    """
    # add ID checking to prevent doubling up
    def boost(self, boost):
        """
        Increase or lower stats in battle
        amount will be an integeral amount
        20 translates to 20%
        """
        mult = 1 + self.get_stat("potency") / 100
        
        found = False
        statNum = 0
        while statNum < len(self.stats) and not found:
            if self.stats[statNum].name == boost.stat_name:
                found = True
                self.stats[statNum].boost(boost)
            statNum += 1
        if not found:
            Dp.add("STAT NOT FOUND: " + name)
            Dp.dp()
    
    def heal(self, percent):
        """
        Restores HP.
        Converts an INTEGER
        to a percentage.
        """
        mult = 1 + self.get_stat("potency") / 100
        healing = self.get_stat("HP") * (float(percent) / 100)
        self.HP_rem = self.HP_rem + healing * mult
        
        Op.add(self.name + " healed " + str(int(healing)) + " HP!")
        Op.dp()
                
        if self.HP_rem > self.get_stat("HP"):
            self.HP_rem = self.get_stat("HP")
    
    def harm(self, percent):
        mult = 1 - self.get_stat("potency") / 100
        harming = self.get_stat("HP") * (float(percent) / 100)
        self.HP_rem = int(self.HP_rem - harming * mult)
        Op.add(self.name + " took " + str(int(harming)) + " damage!")
        Op.dp()
        
    def direct_dmg(self, dmg):
        self.HP_rem -= dmg
        self.HP_rem = int(self.HP_rem)
    
    def gain_energy(self, amount):
        """
        Increase your energy.
        """
        self.energy = self.energy + amount
        
        if self.energy > self.get_stat("energy"):
            self.energy = self.get_stat("energy")
        
        self.energy = int(self.energy)
    
    def lose_energy(self, amount):
        """
        Decrease your energy
        """
        self.energy = self.energy - amount
        if self.energy < 0:
            self.energy = 0
    
    # stat.display_data in here
    def update(self):
        self.update_action_registers()
        for action in self.on_update_actions:
            action["function"]()
        
        self.gain_energy(self.get_stat("energy") * 0.15)
        for stat in self.stats:
            stat.update()
            stat.display_data();
    
    """
    Damage calculation
    """
    def calc_DMG(self, attacker, attack_used):
        """
        MHC is not checked here so that it doesn't
        mess with AI
        """
        damage = 0
        for damage_type, value in attack_used.damages.items():
            damage += value * (attacker.get_stat(damage_type + " damage multiplier") / self.get_stat(damage_type + " damage reduction"))
        damage *= attacker.get_stat("control") / self.get_stat("resistance")
        
        if attacker.team.switched_in:
            damage = damage * 0.75
            
        return damage
    
    def take_DMG(self, attacker, attack_used):
        dmg = self.calc_DMG(attacker, attack_used)
        dmg = dmg * attack_used.calc_MHC()
        Op.add(attacker.name + " struck " + self.name)
        Op.add("for " + str(int(dmg)) + " damage")
        Op.add("using " + attack_used.name + "!")
        Op.dp()
        
        event = OnHitEvent("Attack", attacker, self, attack_used, dmg)
        event.display_data()
        
        for passive in self.on_hit_taken_actions:
            passive["function"](event)
        
        for passive in attacker.on_hit_given_actions:
            passive["function"](event)
        
        self.direct_dmg(dmg)
    
    def check_if_KOed(self):
        """
        Am I dead yet?
        """
        return self.HP_rem <= 0
    
    def generate_stat_code(self):
        """
        Generates a sequence used
        during file reading in order
        to copy stats from one play
        session to the next
        """
        ret = "s"
        for stat in STATS:
            ret += "/" + str(self.get_stat_data(stat).base_value - 20)
        
        return ret
    
    def read_stat_code(self, code):
        """
        Used to load a stat spread
        via a string
        """
        # 0th element is 's'
        new_stat_bases = []
        broken_down_code = code.split('/')
        broken_down_code = broken_down_code[1:]
        Dp.add(broken_down_code)
        Dp.dp()
        ind = 0
        while ind < 5:
            new_stat_bases.append(int(float(broken_down_code[ind])))
            ind += 1
        
        self.set_stat_bases(new_stat_bases)
    
    def generate_save_code(self):
        """
        Used to get all data on this
        character
        """
        ret = [self.generate_stat_code]
        for passive in self.passives:
            ret.append(passive.generate_save_code())
        return ret
    
class PlayerCharacter(AbstractCharacter):
    def __init__(self, name, data, level):
        super(self.__class__, self).__init__(name, data, level)
        self.attack_customization_points = 0
        self.passive_customization_points = 0
        self.stat_customization_points = 0
    
    def choose_attack(self):
        attack_options = []
        for attack in self.attacks:
            if attack.can_use():
                attack_options.append(attack)
        
        choose("What attack do you wish to use?", attack_options).use()
    
    """
    Post-battle actions:
    Occur after battle
    """                
    def gain_XP(self, amount):
        """
        Give experience.
        Caps at the most XP required for a battle
        (Can't level up twice after one battle)
        """
        self.XP = self.XP + amount
        if self.XP >= self.level * 10: 
            if self.level < self.level_set * 5:
                Op.add(self.name + " leveled up!")
                self.level_up()
            else:
                Op.add(self.name + " is being held back... perhaps a special item will help?")
            Op.dp()
    
    def level_up(self):
        """
        Increases level
        """
        self.XP = 0
        self.level += 1
        self.attack_customization_points += 1
        self.passive_customization_points += 1
        self.stat_customization_points += 1
        self.calc_stats()
        self.HP_rem = self.get_stat("HP")
        self.display_data()
    
    def plus_level_set(self):
        """
        Increases your 
        level cap by 5
        """
        self.level_set = self.level_set + 1
    
    """
    Character management
    """
    
    def modify_stats(self):
        for stat in self.stats:
            stat.reset_boosts()
        self.calc_stats()
        self.display_mutable_stats()
        
        self.get_stat_data(choose("Which stat do you want to increase by 5%?", STATS)).base_value += 1
        self.get_stat_data(choose("Which stat do you want to decrease by 5%?", STATS)).base_value -= 1
        
        self.calc_stats()
        self.display_mutable_stats()
        self.stat_customization_points -= 1
    
    def choose_items(self):
        self.display_items()
        
        if choose("Do you wish to change these items?", ("yes", "no")) == "yes":
            for item in self.equipped_items:
                item.unequip()
            
            items = self.team.get_available_items()
            while (len(self.equipped_items) < 3) and (len(items) is not 0):
                item = choose("Which item do you want to equip?", items)
                item.equip(self)
                self.equipped_items.append(item)
                items = self.team.get_available_items()
    
    def choose_passive_to_customize(self):
        choose("Which passive do you want to modify?", self.passives).customize()
        self.passive_customization_points -= 1
    
    def choose_attack_to_customize(self):
        choose("Which attack do you want to modify?", self.attacks).customize()
        self.attack_customization_points -= 1
    
    def customize(self):
        options = ["Quit"]
        
        if len(self.team.inventory) > 0:
            options.append("Items")
        
        if self.passive_customization_points > 0:
            options.append("Passive")
        
        if self.attack_customization_points > 0:
            options.append("Attack")
        
        if self.stat_customization_points > 0:
            options.append("Stat")
        
        options.reverse()
        
        choice = choose("What do you want to modify?", options)
        
        if choice == "Items":
            self.choose_items()
        
        elif choice == "Passive":
            self.choose_passive_to_customize()
        
        elif choice == "Attack":
            self.choose_attack_to_customize()
        
        elif choice == "Stat":
            self.modify_stats()

class EnemyCharacter(AbstractCharacter):
    def __init__(self, name, level):
        super(self.__class__, self).__init__(name, enemies[name], level)
    
    """
    AI stuff
    """
    def best_attack(self):
        best = self.attacks[0]
        highest_dmg = 0
        Dp.add("----------")
        for attack in self.attacks:
            if attack.can_use():
                dmg = self.team.enemy.active.calc_DMG(self, attack)
                if dmg > highest_dmg:
                    best = attack
                    highest_dmg = dmg
                Dp.add("Damge with " + attack.name + ": " + str(dmg))
        Dp.add("----------")
        Dp.dp()
        return best
    
    def what_attack(self):
        """
        Used to help the AI
        choose what attack
        to use
        """
        if self.team.switched_in:
            sw = 0.75
        else:
            sw = 1.0
        
        """
        Can you get multiple KOes?
        """
        """
        for attack in self.attacks:
            if not attack.can_use(self) or not type(attack) == type(AllAttack("test", 0)):
                continue
            koes = 0
            for member in self.team.enemy.members_rem:
                if member.calc_DMG(self, attack) * sw >= member.HP_rem:
                    koes += 1
            if koes >= 2:
                return attack
        """
        """
        Can you get a KO?
        """
        can_ko = []
        for attack in self.attacks:
            if attack.can_use():
                if self.team.enemy.active.calc_DMG(self, attack) * sw >= self.team.enemy.active.HP_rem:
                    can_ko.append(attack)
            
        if len(can_ko) == 1:
            return can_ko[0]
        """
        If you cannot KO...
        """
        return self.best_attack()
    
    def choose_attack(self):
        self.what_attack().use()


"""
Teams
"""
class AbstractTeam(object):
    """
    Teams are used to group characters
    together so that the program knows
    who are enemies, and who are allies.
    """
    def find_enemy(self, teams):
        """
        Take a list of teams 
        (from Battle), and
        return the one that 
        is not self.
        """
        for team in teams:
            if team != self:
                return team
    
    # balance this later
    def xp_given(self):
        """
        How much xp will be given
        once this team is
        defeated.
        """
        xp = 0
        for member in self.use:
            xp += member.level * 10
        return xp / len(self.use)
    
    def is_up(self):
        """
        Use to see if your team still exists
        """
        return len(self.members_rem) != 0
    
    def one_left(self):
        """
        Detects when you have only one member left
        """
        return len(self.members_rem) == 1
    
    def init_active(self):
        """
        Elect a leader
        """
        self.active = self.use[0]
            
    def switch(self, member):
        """
        You're up!
        """
        self.active = member
    
    def initialize(self):
        """
        Ready the troops!
        """
        self.members_rem = []
        for member in self.use:
            member.init_for_battle()
            self.members_rem.append(member)
        self.init_active()
    
    def list_members(self):
        """
        Display the data
        of each member
        of the team
        """
        Op.add(self.name)
        Op.dp(False)
        for member in self.team:
            member.display_data()
    
    def display_data(self):
        """
        Show info for a team
        """
        Op.add(self.name)
        for member in self.members_rem:
            Op.add("* " + member.name + " " + str(int(member.HP_rem)) + "/" + str(int(member.get_stat("HP"))))
        Op.add("Currently active: " + self.active.name)
        self.active.display_mutable_stats()
        Op.add(self.active.name + "'s Energy: " + str(self.active.energy))
        Op.add("Active enemy: " + self.enemy.active.name + " " + str(int(self.enemy.active.HP_rem)) + "/" + str(int(self.enemy.active.get_stat("HP"))))
        Op.dp()
        
    def do_turn(self):
        """
        This is where stuff happens
        """
        new_members_rem = []
        for member in self.members_rem:
            if not member.check_if_KOed():
                new_members_rem.append(member)
                member.update()
            else:
                Op.add(member.name + " is out of the game!")
                Op.dp()
        self.members_rem = new_members_rem
        
        if self.active.check_if_KOed() and self.is_up():
            self.choose_switchin()
        
        if self.is_up():
            self.switched_in = False
            self.choose_action()

class PlayerTeam(AbstractTeam):
    def __init__(self, name, member):
        self.team = []
        self.name = name
        self.team.append(PlayerCharacter(member["name"], member["data"], member["level"]))
        self.inventory = []
        for member in self.team:
            member.team = self
    
    """
    Choices are made using these functions
    """                 
    def choose_switchin(self):
        """
        Who will fight?
        """
        choices = []
        for member in self.members_rem:
            if member != self.active:
                choices.append(member)
        
        self.switch(choose("Who do you want to bring in?", choices))
            
        Op.add(self.active.name + " up!")
        Op.dp()
                                                                        
    def choose_action(self):
        """
        What to do, what to do...
        """
        self.display_data()
        choices = ["Attack"]
        
        if not self.one_left():
            choices.append("Switch")
        
        if choose("What do you wish to do?", choices) == "Switch":
            self.choose_switchin()
            self.switched_in = True
        self.active.choose_attack()
    
    """
    Customization options
    """
    def obtain(self, item):
      self.inventory.append(item)
    
    def get_available_items(self):
        new_array = []
        for item in self.inventory:
            if not item.equipped:
                new_array.append(item)
        return new_array
    
    def customize(self):
        self.team[0].customize()
    
class EnemyTeam(AbstractTeam):
    def __init__(self, name, members):
        self.team = []
        self.name = name
        
        members = to_list(members)
        for new_member in members:
            self.team.append(EnemyCharacter(new_member["name"], new_member["level"]))
        for member in self.team:
            member.team = self
    
    """
    AI stuff
    BENCHIT NEEDS FIX
    general improvements needed
    """
    def should_switch(self):
        """
        First, check if our active can KO
        """
        if self.one_left():
            return "Attack"
        if self.enemy.active.calc_DMG(self.active, self.active.best_attack()) >= self.enemy.active.HP_rem:
            return "Attack"
        """
        # check if your active can benchhit
        if self.active.special.act_any_all != "act":
            for member in self.enemy.members_rem:
                if member.calc_DMG(self.active, self.active.special) >= member.HP_rem and self.active.can_spec():
                    if debug:
                        print(self.active.name + " can KO " + member.name + " with " + self.active.special.name)
                     return "Attack"
        """
        """
        Second, check if an ally can KO 
        """
        for member in self.members_rem:
            if self.enemy.active.calc_DMG(member, member.best_attack()) * 0.75 >= self.enemy.active.HP_rem:
                return "Switch"
        
        # Default
        return "Attack"
        
    # comment     
    def who_switch(self):
        """
        Used to help the AI
        decide who to switch in
        """
        
        """
        Can anyone KO?
        """
        can_ko = []
        for member in self.members_rem:
            if self.enemy.active.calc_DMG(member, member.best_attack()) * 0.75 >= self.enemy.active.HP_rem:
                can_ko.append(member)
        
        for member in can_ko:
            Dp.dd(member.name)
        
        Dp.dd("can KO")
        Dp.dp()
        
        """
        If one person can KO,
        bring them in.
        If nobody can,
        change nothing.
        If someone can KO,
        only use them.
        """
        if len(can_ko) == 1:
            return can_ko[0]
        elif len(can_ko) == 0:
            array = self.members_rem
        else:
            array = can_ko
                
        rand = random.randint(0, len(array) - 1)
        return array[rand]    

    """
    Choices are made using these functions
    """                 
    def choose_switchin(self):
        """
        Who will fight?
        """
        self.switch(self.who_switch())
            
        Op.add(self.active.name + " up!")
        Op.dp()
                                                                        
    def choose_action(self):
        """
        What to do, what to do...
        """
        self.display_data()
        
        choices = ["Attack"]
        
        if not self.one_left():
            choices.append("Switch")
            
        if self.should_switch() == "Switch":
            self.choose_switchin()
            self.switched_in = True
        self.active.choose_attack()



class Weather(object):
    """
    This is what makes Maelstrom unique!
    Weather provides in-battle effects
    that alter the stats of characters
    """
    def __init__(self, type, intensity, msg):
        """
        The type determines what sort of effect will
        be applied to all participants in a battle.
        The intensity is how potent the effect will be.
        The msg is what text will show to help
        the player determine the weather.
        """
        self.type = type
        self.intensity = intensity
        self.msg = msg
            
    def do_effect(self, affected):
        """
        Apply stat changes 
        to a team
        """
        
        if self.type == "Lightning":
            for person in affected:
                person.gain_energy(int(self.intensity/20))
                
        if self.type == "Wind":
            for person in affected:
                person.boost("STR", self.intensity/100, 3)
        
        if self.type == "Hail":
            for person in affected:
                person.take_dmg(self.intensity)
        
        if self.type == "Rain":
            for person in affected:
                person.heal(self.intensity)
                     
    def disp_msg(self):
        """
        Print a message showing
        the weather condition
        """
        Op.add(self.msg)
        Op.dp()

class Battle(object):
    """
    The Battle class pits 2 teams
    against eachother, 
    initializing them
    and the weather.
    """
    def __init__(self, name, description, script, end, team_size, weather_list, rewards = None):
        """
        Maximum team size,
        Weather should be improved
        """
        self.teams = []
        self.name = name
        self.description = description
        self.script = Story(script)
        self.final_act = Story(end)
        self.team_size = team_size
        self.forecast = to_list(weather_list)
        self.rewards = to_list(rewards)
    
    def display_data(self):
        Op.add([self.name, self.description])
        
        for member in self.teams[0].use:
            Op.add("* " + member.name + " LV " + str(member.level) + " " + member.element)
        Op.dp(False)
    
    def load_team(self, team):
        """
        Add a team 
        to the battle
        """
        if len(self.teams) < 2:
            self.teams.append(team)
            team.use = team.team
        
    # stuff down here
    # add random loot
    def check_winner(self):
        """
        Runs when one
        teams loses all
        members.
        """
        for team in self.teams:
            if team.is_up():
                winner = team
        Op.add(winner.name + " won!")
        Op.dp()
        """
        if not winner.AI:
            self.final_act.print_story()
            for reward in self.rewards:
                if reward == None:
                    continue
                reward.give(winner)
        """
    
    def begin(self):
        """
        Prepare both teams
        for the match.
        """
        self.script.print_story()
        
        for team in self.teams:
            team.initialize()
            team.enemy = team.find_enemy(self.teams)
            Op.add(team.name)
            
            for member in team.use:
                member.display_data()
        if self.forecast[0] == None:
            self.weather = Weather(None, 0, "The land is seized by an undying calm...")
        else:
            if len(self.forecast) == 1:
                num = 0
            else:
                num = random.randrange(0, len(self.forecast) - 1)
                self.weather = self.forecast[num]
        self.weather.disp_msg()
    
    def end(self):
        """
        The stuff that takes place after battle
        """
        for team in self.teams:
            if team.__class__ == PlayerTeam:
                for member in team.use:
                    xp = team.enemy.xp_given()
                    member.gain_XP(xp)
                                    
    def play(self):
        """
        Used to start
        the battle
        """
        self.begin()
        
        while self.teams[0].is_up() and self.teams[1].is_up():
            for team in self.teams:
                if team.is_up():
                    self.weather.do_effect(team.members_rem)
                    team.do_turn()
                # this check is needed if the 
                #first team beats the second one
                if not team.is_up():
                    break            
        self.check_winner()
        self.end()

from utilities import *
from navigate import Story