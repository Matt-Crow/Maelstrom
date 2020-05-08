from stat_classes import Stat, Boost
import pprint
from utilities import ELEMENTS, get_hit_perc, roll_perc, Dp
from upgradable import AbstractUpgradable
from output import Op


class AbstractActive(AbstractUpgradable):
    """
    The actives all characters can use
    """


    # formula functions are given at the end of this file
    def __init__(self, name: str, energy_cost = 5):
        """
        Don't invoke this, instead call AbstractActive.read_json
        on a dictionary containing the Active's data
        """
        super(AbstractActive, self).__init__(name)
        self.set_type("AbstractActive")
        self.add_attr("damage multiplier", Stat("damage multiplier", mult_f, 0))

        for element in ELEMENTS:
            self.add_attr(element + " damage weight", Stat(element + " damage weight", dmg_weight, 0))

        self.add_attr("cleave", Stat("cleave", cleave_form, 0))

        self.add_attr("miss chance", Stat("miss chance", miss_form, 0))
        self.add_attr("crit chance", Stat("crit chance", crit_form, 0))
        self.add_attr("miss mult", Stat("miss mult", miss_mult_form, 0))
        self.add_attr("crit mult", Stat("crit mult", crit_mult_form, 0))
        self.energy_cost = energy_cost

        self.side_effects = []
        self.damages = {}


    @staticmethod
    def read_json(json: dict) -> 'AbstractActive':
        """
        Reads a JSON object as a dictionary, then converts it to an Active
        """
        #print("JSON:")
        #pprint.pprint(json)

        #some way to auto-do this?
        name = json.get("name", "NAME NOT FOUND")
        rtype = json.get("type", "TYPE NOT FOUND")
        custom_points = int(json.get('customPoints', 0))

        ret = None
        if rtype == "AbstractActive":
            ret = AbstractActive(name)
        else:
            ret = MeleeAttack(name)

        for k, v in json.items():
            if type(v) == type({}) and v.get('type', 'NO TYPE') == 'Stat':
                ret.set_base(k, int(v.get('base', 0)))

        ret.customPoints = custom_points

        return ret

    def set_damage_distributions(self, new_dists: dict):
        """
        new_dist should be a dict
        """
        for k, v in new_dists.items():
            self.set_base(k, v)

    def add_side_effect(self, boost, chance = 100):
        """
        Add a boost to inflict upon hitting
        """
        self.side_effects.append({"effect": boost, "chance":chance})

    def set_cleave(self, base: int):
        """
        Sets the cleave base for this
        """
        self.set_base("cleave", base)

    def set_user(self, user):
        super(AbstractActive, self).set_user(user)
        self.distribute_damage()

    def initForBattle(self):
        self.calc_all()
        self.distribute_damage()
        for side_effect in self.side_effects:
            side_effect["effect"].reset()


    def distribute_damage(self):
        self.calc_all()
        lv = 1 if self.user is None else self.user.level
        total = get_hit_perc(lv) * self.get_stat("damage multiplier")
        split_between = 0
        self.damages = {}
        for element in ELEMENTS:
            split_between += self.get_stat(element + " damage weight")
        for element in ELEMENTS:
            self.damages[element] = total / split_between * self.get_stat(element + " damage weight")

    def total_dmg(self):
        ret = 0
        for damage in self.damages.values():
            ret += damage
        return ret

    def getDisplayData(self):
        self.initForBattle()
        ret = [self.type + " " + self.name]

        for type, value in self.damages.items():
            ret.append('\t' + type + " damage: " + str(int(value)))

        ret.append("\tCritical hit chance: " + str(self.get_stat("crit chance")) + "%")
        ret.append("\tMiss chance: " + str(self.get_stat("miss chance")) + "%")
        ret.append("\tCritical hit multiplier: " + str(int(self.get_stat("crit mult") * 100)) + "%")
        ret.append("\tMiss multiplier: " + str(int(self.get_stat("miss mult") * 100)) + "%")
        ret.append("\tCleave damage: " + str(int(self.get_stat("cleave") * 100)) + "% of damage from initial hit")
        ret.append("\tSIDE EFFECTS:")
        for side_effect in self.side_effects:
            ret.append('\t\t' + str(side_effect["chance"]) + "% chance to inflict")
            for line in side_effect["effect"].getDisplayData():
                ret.append('\t\t' + line)

        return ret

    def can_use(self):
        return self.user.energy >= self.energy_cost

    def calc_MHC(self):
        """
        Used to calculate hit type
        """
        ret = 1.0

        rand = roll_perc(self.user.get_stat("luck"))
        Dp.add(["rand in calc_MHC: " + str(rand), "Crit: " + str(100 - self.get_stat("crit chance")), "Miss: " + str(self.get_stat("miss chance"))])
        Dp.dp()
        if rand <= self.get_stat("miss chance"):
            Op.add("A glancing blow!")
            ret = self.get_stat("miss mult")

        elif rand >= 100 - self.get_stat("crit chance"):
            Op.add("A critical hit!")
            ret = self.get_stat("crit mult")
        Op.display()

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
        self.user.loseEnergy(self.energy_cost)
        if self.get_stat("damage multiplier") is not 0:
            self.user.team.enemy.active.struckBy(self.user, self)
            self.apply_side_effects_to(self.user.team.enemy.active)
        if self.get_stat("cleave") is not 0.0:
            for enemy in self.user.team.enemy.members_rem:
                if enemy is not self.user.team.enemy.active:
                    enemy.takeDmg(self.total_dmg() * self.get_stat("cleave"))
                    self.apply_side_effects_to(enemy)

    """
    Returns the default actives that every
    character can use
    """
    @staticmethod
    def getDefaults(element: str) -> list:
        bolt = AbstractActive.read_json({
            'name' : element + ' bolt',
            'type' : 'AbstractActive',
            'cleave' : -5,
            'crit chance' : -2,
            'damage multiplier' : 7
        })

        slash = MeleeAttack("Slash")
        jab = AbstractActive.read_json({
            "name" : "Jab",
            "type" : "MeleeAttack",
            "miss chance" : {
                'type': 'Stat',
                'base': -5,
                'name': 'miss chance'
            },
            "crit chance" : {
                'type': 'Stat',
                'base': 5,
                'name': 'crit chance'
            },
            "miss mult" : {
                'type': 'Stat',
                'base': -5,
                'name': 'miss mult'
            },
            "crit mult" : {
                'type': 'Stat',
                'base': 5,
                'name': 'crit mult'
            }
        })
        slam = AbstractActive.read_json({
            "name" : "Slam",
            "type" : "MeleeAttack",
            "damage multiplier" : {
                'type': 'Stat',
                'base': 5,
                'name': 'damage multiplier'
            },
            "miss chance" : {
                'type': 'Stat',
                'base': -5,
                'name': 'miss chance'
            }
        })

        return [bolt, slash, jab, slam]


class MeleeAttack(AbstractActive):
    def __init__(self, name):
        super(MeleeAttack, self).__init__(name, 0)
        self.set_type("MeleeAttack")


#these are the formulae used by stat calculations
def mult_f(base: int) -> float:
    """
    The formula used to calculate damage multipliers

    will balance later
    """
    return 1.0 + base * 0.05


def dmg_weight(base: int) -> float:
    """
    The formula for damage weight

    Damage weight is how much of the actives's total damage will be devoted to
    a specific element.
    For example,
    by default, the weights are 10 for each element, so the total damage would be evenly divided.
    But, if their were 4 elements, weighted at 10, 10, 10, and 20; 20% of the total damage would go to each of the first 3,
    and the remaining 40% would go to the last
    """
    return 11 + base #minimum that doesn't have divide by zero


def cleave_form(base: int) -> float:
    """
    The formula used to calculate "cleave damage":
    whenever you attack an enemy, the attack will
    deal some percentage of that damage to each other
    enemy.

    Note that this does not decrease the damage of the initial hit
    """
    return 0.25 + base * 0.05


def crit_form(base: int) -> int:
    """
    Used to calculate the chance of a critical hit based on the given base
    """
    return 10 + base


def miss_form(base: int) -> int:
    """
    Used to calculate the chance of a miss based on the given base
    """
    return 10 - base


def crit_mult_form(base: int) -> float:
    """
    Used to calculate the multiplier for critical hits
    """
    return 1.5 + 0.05 * base


def miss_mult_form(base: int) -> float:
    """
    Used to calculate the multiplier for misses
    """
    return 0.5 + 0.05 * base
