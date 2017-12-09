from utilities import *
from enemies import *
from stat_classes import *
from attacks import *
from passives import *
from item import *
from events import *

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
        
        self.attacks = [ActAttack(self.element + " bolt", 1.75, 5)]
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
        
        p = Threshhold("Threshhold test", 100, Boost("resistance", 20, 1, "Threshhold test"))
        self.passives.append(p)
        p.set_user(self)
        
        o = OnHitGiven("OnHitGivenTest", 25, Boost("luck", 20, 5, "OnHitGivenTest"))
        self.passives.append(o)
        o.set_user(self)
        
        h = OnHitTaken("OnHitTakenTest", 25, Boost("control", -20, 1, "OnHitTakenTest"))
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
        
        check_set = None
        set_total = 0
        for item in self.equipped_items:
            item.apply_boosts()
            if item.set != None:
                if check_set == None:
                    check_set = item.set
                if item.set == check_set:
                    set_total += 1
            if set_total == 3:
                check_set.f(self)
        
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
        Op.dp()
    
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
        self.direct_dmg(harming * mult)
        Op.add(self.name + " took " + str(int(harming * mult)) + " damage!")
        Op.dp()
        
    def direct_dmg(self, dmg):
        self.HP_rem -= dmg
        self.HP_rem = int(self.HP_rem)
        self.team.update_members_rem()
    
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
            #stat.display_data();
    
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
        ret = self.name
        ret += " "
        ret += self.level
        ret += self.generate_stat_code
        for passive in self.passives:
            ret += passive.generate_save_code()
        return ret
    
class PlayerCharacter(AbstractCharacter):
    def __init__(self, name, data, level):
        super(self.__class__, self).__init__(name, data, level)
        self.attack_customization_points = 0
        self.passive_customization_points = 0
        self.stat_customization_points = 0
        self.item_customization_points = 0
    
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
        self.item_customization_points += 1
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
        
        if len(self.equipped_items) == 0 or choose("Do you wish to change these items?", ("yes", "no")) == "yes":
            for item in self.equipped_items:
                item.unequip()
            
            items = self.team.get_available_items()
            
            if len(items) <= 3:
                for item in items:
                    item.equip(self)
                    self.equipped_items.append(item)
            else:
                for item in items:
                    item.display_data()
            
            items = self.team.get_available_items()
            while (len(self.equipped_items) < 3) and (len(items) is not 0):
                item = choose("Which item do you want to equip?", items)
                item.equip(self)
                self.equipped_items.append(item)
                items = self.team.get_available_items()
            
            self.display_items()
    
    def choose_passive_to_customize(self):
        for passive in self.passives:
            passive.display_data()
        choose("Which passive do you want to modify?", self.passives).customize()
        self.passive_customization_points -= 1
    
    def choose_attack_to_customize(self):
        for attack in self.attacks:
            attack.display_data()
        choose("Which attack do you want to modify?", self.attacks).customize()
        self.attack_customization_points -= 1
    
    def choose_item_to_customize(self):
        for item in self.team.inventory:
            item.display_data()
        choose("Which item do you want to modify?", self.team.inventory).generate_random_enh()
        self.item_customization_points -= 1
    
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
            item_actions = ["equip"]
            if self.item_customization_points > 0:
                item_actions.append("augment")
            if choose("Do you want to equip items, or augment them?", item_actions) == "equip":
                self.choose_items()
            else:
                self.choose_item_to_customize()
        
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