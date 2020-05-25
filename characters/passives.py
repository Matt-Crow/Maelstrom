from utilities import *
from stat_classes import Stat, Boost

from customizable import AbstractCustomizable
from events import HIT_GIVEN_EVENT, HIT_TAKEN_EVENT, UPDATE_EVENT
from output import Op


"""
Passives
"""
class AbstractPassive(AbstractCustomizable):
    """
    kwargs:
    - name : str
    - type : str
    - boostedStat : str
    - targetsUser : boolean (defaults to True)
    - stats : dict{str, int}, defaults to 0 for each stat not given
        - status level (defaults to 0.25)
        - status duration (defaults to 3)
    """
    def __init__(self, **kwargs):
        super(AbstractPassive, self).__init__(**dict(kwargs, type=kwargs.get("type", "AbstractPassive")))
        self.boostedStat = kwargs["boostedStat"]
        self.targetsUser = kwargs.get("targetsUser", True)

        self.addStat(Stat("status level", lambda base : 0.25 + 0.025 * base, kwargs.get("stats", {}).get("status level", 0)))
        self.addStat(Stat("status duration", lambda base : 3 + int(float(base) / 5), kwargs.get("stats", {}).get("status duration", 0)))

        self.addSerializedAttributes(
            "boostedStat",
            "targetsUser"
        )

    @classmethod
    def deserializeJson(cls, jdict: dict)->"AbstractPassive":
        ret = None
        type = jdict["type"]
        if type == "Threshhold Passive":
            ret = Threshhold(**jdict)
        elif type == "On Hit Given Passive":
            ret = OnHitGiven(**jdict)
        elif type == "On Hit Taken Passive":
            ret = OnHitTaken(**jdict)
        else:
            raise Exception("Type not found for AbstractPassive: " + type)
        return ret

    """
    Returns the Boost this will inflict
    """
    def getBoost(self)->"Boost":
        lv = self.getStatValue("status level")
        if not self.targetsUser:
            lv = -lv

        return Boost(self.boostedStat, self.getStatValue("status level"), self.getStatValue("status duration"), self.name)

    """
    Applies this' boost
    """
    def applyBoost(self):
        target = self.user if self.targetsUser else self.user.team.enemy.active
        target.boost(self.getBoost())

    """
    Returns the default passives
    """
    @staticmethod
    def getDefaults() -> list:
        p = Threshhold(
            name="Threshhold test",
            boostedStat="resistance",
        )

        o = OnHitGiven(
            name="On Hit Given Test",
            boostedStat="luck",
        )

        h = OnHitTaken(
            name="On Hit Taken Test",
            boostedStat="control",
            targetsUser=False
        )

        return [p, o, h]


class Threshhold(AbstractPassive):
    """
    Additional kwargs:
    - stats {str, int}:
        - threshhold (defaults to 25%)
    """
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**dict(kwargs, type="Threshhold Passive"))
        self.addStat(Stat("threshhold", lambda base : 0.25 + base * 0.025, kwargs.get("stats", {}).get("threshhold", 0)))

    def initForBattle(self):
        self.user.addActionListener(UPDATE_EVENT, self.checkTrigger)

    def checkTrigger(self, updated):
        Dp.add("Checking trigger for " + self.name)
        Dp.add(str(self.getStatValue("threshhold") * 100) + "% threshhold")
        Dp.add(str(updated.getHpPerc()) + "% user health")
        if updated.getHpPerc() <= self.getStatValue("threshhold"):
            Dp.add("activated")
            self.applyBoost()
        Dp.dp()

    """
    returns a text representation of this object
    """
    def getDisplayData(self) -> list:
        target = "user" if self.targetsUser else 'active enemy'
        return [
            self.name + ":",
            '\tInflicts ' + target + ' with a ' + str(self.getStatValue("status level") * 100) + '% bonus',
            '\tto their ' + self.boostedStat + ' stat',
            '\tfor ' + str(self.getStatValue('status duration')) + ' turns',
            '\twhen the user is at or below ' + str(self.getStatValue('threshhold') * 100) + '% of their maximum hit points.'
        ]


class OnHitGiven(AbstractPassive):
    """
    Additional kwargs:
    - stats : {str, int}:
        - chance (defaults to 25%)
    """
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**dict(kwargs, type="On Hit Given Passive"))
        self.addStat(Stat("chance", lambda base : 25 + int(base * 2.5), kwargs.get("stats", {}).get("chance", 0)))

    def initForBattle(self):
        self.user.addActionListener(HIT_GIVEN_EVENT, self.checkTrigger)

    def checkTrigger(self, onHitEvent):
        rand = roll_perc(self.user.getStatValue("luck"))
        Dp.add("Checking trigger for " + self.name)
        Dp.add("Need to roll " + str(100 - self.getStatValue('chance')) + " or higher to activate")
        Dp.add("Rolled " + str(rand))
        if rand > 100 - self.getStatValue('chance'):
            Dp.add("activated")
            self.applyBoost()
        Dp.dp()

    """
    returns a text representation of this object
    """
    def getDisplayData(self) -> list:
        target = "user" if self.targetsUser else "that opponent"
        return [
            self.name + ":",
            "\tWhenever the user strikes an opponent, has a " + str(self.getStatValue("chance")) + '% chance to',
            '\tinflict ' + target + ' with a ' + str(self.getStatValue('status level') * 100) + '% bonus',
            '\tto their ' + self.boostedStat + ' stat',
            '\tfor ' + str(self.getStatValue('status duration')) + ' turns'
        ]


class OnHitTaken(AbstractPassive):
    """
    Additional kwargs:
    - stats : {str, int}:
        - chance (defaults to 25%)
    """
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**dict(kwargs, type="On Hit Taken Passive"))
        self.addStat(Stat("chance", lambda base : 25 + int(base * 2.5), kwargs.get("stats", {}).get("chance", 0)))

    def initForBattle(self):
        self.user.addActionListener(HIT_TAKEN_EVENT, self.checkTrigger)

    def checkTrigger(self, onHitEvent):
        rand = roll_perc(self.user.getStatValue("luck"))
        Dp.add("Checking trigger for " + self.name)
        Dp.add("Need to roll " + str(100 - self.getStatValue('chance')) + " or higher to activate")
        Dp.add("Rolled " + str(rand))
        if rand > 100 - self.getStatValue('chance'):
            Dp.add("activated")
            self.applyBoost()
        Dp.dp()

    """
    returns a text representation of this object
    """
    def getDisplayData(self) -> list:
        target = 'user' if self.targetsUser else 'the attacker'
        return [
            self.name + ':',
            '\tWhenever the user is struck by an opponent, has a ' + str(self.getStatValue('chance')) + '% chance to',
            '\tinflict ' + target + ' with a ' + str(self.getStatValue('status level') * 100) + '% bonus',
            '\tto their ' + self.boostedStat + ' stat',
            '\tfor ' + str(self.getStatValue('status duration')) + ' turns'
        ]
