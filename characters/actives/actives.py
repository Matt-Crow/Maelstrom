from stat_classes import Stat, Boost
from utilities import roll_perc
from customizable import AbstractCustomizable
from characters.actives.activeStats import ActiveStatFactory
from inputOutput.output import debug
from util.stringUtil import entab


"""
This module handles active abilities that characters can use
"""

"""
Calculates the average amount of damage an attack should do to a target at a
given level
"""
def getDmgPerc(lv):
    return 16.67 * (1 + lv * 0.05)

class HitType:
    def __init__(self, multiplier, message):
        self.multiplier = multiplier
        self.message = message

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
        statFact = ActiveStatFactory()
        #                                                                     get stat dict, if it has one, else an empty dict
        #self.addStat(Stat("damage multiplier", lambda base: 1.0 + base * 0.05, kwargs.get("stats", {}).get("damage multiplier", 0)))
        #                                                                                                 no damage multiplier? Just do 0
        self.addStat(statFact.makeDamageMultiplier(kwargs.get("stats", {}).get("damage multiplier", 0)))
        self.addStat(Stat("cleave", lambda base: 0.25 + base * 0.05, kwargs.get("stats", {}).get("cleave", 0)))
        self.addStat(Stat("miss chance", lambda base: 10 - base, kwargs.get("stats", {}).get("miss chance", 0)))
        self.addStat(Stat("crit chance", lambda base: 10 + base, kwargs.get("stats", {}).get("crit chance", 0)))
        self.addStat(Stat("miss mult", lambda base: 0.5 + 0.05 * base, kwargs.get("stats", {}).get("miss mult", 0)))
        self.addStat(Stat("crit mult", lambda base: 1.5 + 0.05 * base, kwargs.get("stats", {}).get("crit mult", 0)))

        self.cost = kwargs.get("cost", 5)
        self.damage = getDmgPerc(1) * self.getStatValue("damage multiplier")

        self.addSerializedAttribute("cost")

    def setUser(self, user):
        super(AbstractActive, self).setUser(user)
        self.initForBattle()

    def initForBattle(self):
        self.calcStats()
        lv = 1 if not hasattr(self, "user") else self.user.level
        self.damage = getDmgPerc(lv) * self.getStatValue("damage multiplier")

    def getDisplayData(self)->str:
        self.initForBattle()
        ret = [
            f'{self.name}:',
            entab(f'{int(self.damage)} damage to target'),
            entab(f'all other enemies receive {int(self.getStatValue("cleave") * 100)}% of the damage from the initial hit'),
            entab(f'{self.getStatValue("crit chance")}% chance of scoring a critical hit,'),
            entab(f'for a {int(self.getStatValue("crit mult") * 100)}% damage multiplication'),
            entab(f'{self.getStatValue("miss chance")}% chance of scoring a glancing bow,'),
            entab(f'for a {int(self.getStatValue("miss mult") * 100)}% damage multiplication')
        ]

        return "\n".join(ret)

    def canUse(self):
        return self.user.energy >= self.cost

    """
    Used to calculate hit type
    """
    def getMHCMult(self)->"HitType":

        ret = HitType(1.0, "")

        rand = roll_perc(self.user.getStatValue("luck"))
        debug(f'Crit: {100 - self.getStatValue("crit chance")}')
        debug(f'Miss: {self.getStatValue("miss chance")}')
        debug(f'Rand in getMHCMult: {rand}')
        if rand <= self.getStatValue("miss chance"):
            ret = HitType(self.getStatValue("miss mult"), "A glancing blow!")

        elif rand >= 100 - self.getStatValue("crit chance"):
            ret = HitType(self.getStatValue("crit mult"), "A critical hit!")

        return ret

    def use(self)->str:
        msgs = []

        self.user.loseEnergy(self.cost)
        if self.getStatValue("damage multiplier") is not 0:
            msgs.append(self.user.team.enemy.active.struckBy(self.user, self))

        if self.getStatValue("cleave") > 0:
            for enemy in self.user.team.enemy.membersRem:
                if enemy is not self.user.team.enemy.active:
                    msgs.append(f'cleave damage struck {enemy.name} for {enemy.takeDmg(self.damage * self.getStatValue("cleave"))} damage')

        return "\n".join(msgs)

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
        super(MeleeAttack, self).__init__(**dict(kwargs, type="MeleeAttack", cost=0))
