from utilities import ELEMENTS, STATS
from stat_classes import Stat
from attacks import AbstractActive
from passives import AbstractPassive
from item import Item, ItemSet
from events import *
from upgradable import AbstractUpgradable
from output import Op

"""
Characters
"""
class AbstractCharacter(AbstractUpgradable):
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
        super(AbstractCharacter, self).__init__(name)
        self.max_hp = 100

        self.stats = []
        self.set_stat_bases(data[0])


        for element in ELEMENTS:
            self.add_attr(element + " damage multiplier", Stat(element + " damage multiplier", mult_red_stat, 10))
            self.add_attr(element + " damage reduction", Stat(element + " damage reduction", mult_red_stat, 10))

        self.element = data[1]
        self.level = level
        self.XP = 0

        self.attacks = [AbstractActive.get_default_bolt(self.element)]
        self.passives = []

        self.add_default_actives()
        self.set_passives_to_defaults()
        for attack in self.attacks:
            attack.set_user(self)
        self.equipped_items = []

        self.equip_default_items()

        self.track_attr('attacks')
        self.track_attr('passives')
        self.track_attr('equipped_items')


    def set_stat_bases(self, bases):
        """
        Set the base stat shifts
        """
        # we'll go through 5 stats
        stat_num = 0
        while stat_num < 5:
            self.add_attr(STATS[stat_num], Stat(STATS[stat_num], battle_stat, bases[stat_num]))
            stat_num += 1


    #temporary
    def add_default_actives(self):
        for active in AbstractActive.get_defaults():
            self.attacks.append(active)
            active.set_user(self)
            active.calc_all()

    #temporary
    def set_passives_to_defaults(self):
        for passive in AbstractPassive.get_defaults():
            self.passives.append(passive)
            passive.set_user(self)
            passive.calc_all()

    def equip_default_items(self):
        for item in Item.get_defaults():
            self.equipped_items.append(item)
            item.set_user(self)
            item.equip(self)
            item.calc_all()


    # HP defined here
    def init_for_battle(self):
        """
        Prepare for battle!
        """
        self.reset_action_registers()

        self.calc_all()

        for attack in self.attacks:
            attack.set_user(self)
            attack.init_for_battle()

        for passive in self.passives:
            passive.set_user(self)
            passive.init_for_battle()

        for item in self.equipped_items:
            item.set_user(self)
            item.apply_boosts()

        # this part down here checks if we should get the 3-piece set bonus from our items
        check_set = None
        set_total = 0
        for item in self.equipped_items:
            if item.set_name != None:
                if check_set == None:
                    check_set = item.set_name
                if item.set_name == check_set:
                    set_total += 1
            if set_total == 3:
                ItemSet.get_set_bonus(check_set).f(self)

        self.HP_rem = self.max_hp
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
        return int((float(self.HP_rem) / float(self.max_hp) * 100.0))


    def display_data(self):
        """
        Print info on a character
        """
        self.calc_all()
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
        Op.display()


    def get_short_desc(self):
        """
        returns a short description of the character
        """
        return self.name + " Lv " + str(self.level) + " " + self.element


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
        self.attributes[boost.stat_name].boost(boost)


    def heal(self, percent):
        """
        Restores HP.
        Converts an INTEGER
        to a percentage.
        """
        mult = 1 + self.get_stat("potency") / 100
        healing = self.max_hp * (float(percent) / 100)
        self.HP_rem = self.HP_rem + healing * mult

        Op.add(self.name + " healed " + str(int(healing)) + " HP!")
        Op.display()

        if self.HP_rem > self.max_hp:
            self.HP_rem = self.max_hp

    def harm(self, percent):
        mult = 1 - self.get_stat("potency") / 100
        harming = self.max_hp * (float(percent) / 100)
        self.direct_dmg(harming * mult)
        Op.add(self.name + " took " + str(int(harming * mult)) + " damage!")
        Op.display()

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
        Op.display()

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


"""
Stat formulae,
used to calculate stat values
"""


def mult_red_stat(base: int) -> float:
    """
    passed in as the formula for multiplication and reduction stats
    """
    return (0.5 + 0.05 * base)


def battle_stat(base: int) -> float:
    """
    passed in as the formula for battle stats
    (damage reduction, multiplication, etc)
    """
    return 10.0 + float(base)
