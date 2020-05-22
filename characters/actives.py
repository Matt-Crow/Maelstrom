from stat_classes import Stat, Boost
import pprint
from utilities import ELEMENTS, roll_perc, Dp
from customizable import AbstractCustomizable
from output import Op

def getDmgPerc(lv):
    """
    Calculates how much
    damage an attack should
    do to a target at a given
    level
    """
    return 16.67 * (1 + lv * 0.05)

"""
The actives all characters can use
"""
class AbstractActive(AbstractCustomizable):
    """
    kwargs:
    - type : str
    - name : str
    - cost : int (defaults to 5)
    - stats : dict{str, int}, defaults to 0 for each stat not found.
        - damage multiplier
        - cleave
        - miss chance
        - crit change
        - miss mult
        - crit mult

    """
    def __init__(self, **kwargs):
        super(AbstractActive, self).__init__(**dict(kwargs, type=kwargs.get("type", "AbstractActive")))
        #                                                                     get stat dict, if it has one, else an empty dict
        self.addStat(Stat("damage multiplier", lambda base: 1.0 + base * 0.05, kwargs.get("stats", {}).get("damage multiplier", 0)))
        #                                                                                                 no damage multiplier? Just do 0
        self.addStat(Stat("cleave", lambda base: 0.25 + base * 0.05, kwargs.get("stats", {}).get("cleave", 0)))
        self.addStat(Stat("miss chance", lambda base: 10 - base, kwargs.get("stats", {}).get("miss chance", 0)))
        self.addStat(Stat("crit chance", lambda base: 10 + base, kwargs.get("stats", {}).get("crit chance", 0)))
        self.addStat(Stat("miss mult", lambda base: 0.5 + 0.05 * base, kwargs.get("stats", {}).get("miss mult", 0)))
        self.addStat(Stat("crit mult", lambda base: 1.5 + 0.05 * base, kwargs.get("stats", {}).get("crit mult", 0)))

        self.cost = kwargs.get("cost", 5)
        self.damage = getDmgPerc(1) * self.getStatValue("damage multiplier")

    """
    Reads a JSON object as a dictionary, then converts it to an Active
    """
    @classmethod
    def deserializeJson(cls, jdict: dict)->"AbstractActive":
        ret = None
        type = jdict["type"]

        if type == "AbstractActive":
            ret = AbstractActive(**jdict)
        elif type == "MeleeAttack":
            ret = MeleeAttack(**jdict)
        else:
            raise Exception("Type not found for AbstractActive: " + type)

        return ret

    def setUser(self, user):
        super(AbstractActive, self).setUser(user)
        self.initForBattle()

    def initForBattle(self):
        self.calcStats()
        lv = 1 if not hasattr(self, "user") else self.user.level
        self.damage = getDmgPerc(lv) * self.getStatValue("damage multiplier")

    def getDisplayData(self):
        self.initForBattle()
        ret = [self.type + " " + self.name]
        ret.append("\tdamage: " + str(int(self.damage)))
        ret.append("\tCritical hit chance: " + str(self.getStatValue("crit chance")) + "%")
        ret.append("\tMiss chance: " + str(self.getStatValue("miss chance")) + "%")
        ret.append("\tCritical hit multiplier: " + str(int(self.getStatValue("crit mult") * 100)) + "%")
        ret.append("\tMiss multiplier: " + str(int(self.getStatValue("miss mult") * 100)) + "%")
        ret.append("\tCleave damage: " + str(int(self.getStatValue("cleave") * 100)) + "% of damage from initial hit")

        return ret

    def canUse(self):
        return self.user.energy >= self.cost

    def getMHCMult(self):
        """
        Used to calculate hit type
        """
        ret = 1.0

        rand = roll_perc(self.user.getStatValue("luck"))
        Dp.add(["rand in getMHCMult: " + str(rand), "Crit: " + str(100 - self.getStatValue("crit chance")), "Miss: " + str(self.getStatValue("miss chance"))])
        Dp.dp()
        if rand <= self.getStatValue("miss chance"):
            Op.add("A glancing blow!")
            ret = self.getStatValue("miss mult")

        elif rand >= 100 - self.getStatValue("crit chance"):
            Op.add("A critical hit!")
            ret = self.getStatValue("crit mult")
        Op.display()

        return ret

    def use(self):
        self.user.loseEnergy(self.cost)
        if self.getStatValue("damage multiplier") is not 0:
            self.user.team.enemy.active.struckBy(self.user, self)
        if self.getStatValue("cleave") is not 0.0:
            for enemy in self.user.team.enemy.membersRem:
                if enemy is not self.user.team.enemy.active:
                    enemy.takeDmg(self.damage * self.getStatValue("cleave"))

    """
    Returns the default actives that every
    character can use
    """
    @staticmethod
    def getDefaults(element: str) -> list:
        bolt = AbstractActive(
            name=element+" bolt",
            stats={
                "cleave":-5,
                "crit chance":-2,
                "damage multiplier":7
            }
        )

        slash = MeleeAttack(name="Slash")
        jab = MeleeAttack(
            name="Jab",
            stats={
                "miss chance":-5,
                "crit chance":5,
                "miss mult":-5,
                "crit mult":5
            }
        )
        slam = MeleeAttack(
            name="Slam",
            stats={
                "damage multiplier":5,
                "miss chance":-5
            }
        )

        return [bolt, slash, jab, slam]


class MeleeAttack(AbstractActive):
    def __init__(self, **kwargs):
        super(MeleeAttack, self).__init__(**dict(kwargs, type="MeleeAttack"))
