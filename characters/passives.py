from stat_classes import Stat, Boost
from customizable import AbstractCustomizable
from events import HIT_GIVEN_EVENT, HIT_TAKEN_EVENT, UPDATE_EVENT
from inputOutput.output import debug
from util.stringUtil import entab
from util.utilities import roll_perc

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
        debug(f'Checking trigger for {self.name}')
        debug(f'{(self.getStatValue("threshhold") * 100)}% threshhold')
        debug(f'{updated.getHpPerc()}% user health')
        if updated.getHpPerc() <= self.getStatValue("threshhold") * 100:
            debug("activated")
            self.applyBoost()

    """
    returns a text representation of this object
    """
    def getDisplayData(self) -> str:
        target = "user" if self.targetsUser else 'active enemy'
        desc = [
            f'{self.name}:',
            entab(f'Inflicts {target} with {self.getBoost().getDisplayData()} when the user is at or below {self.getStatValue("threshhold") * 100}% of their maximum HP')
        ]
        return "\n".join(desc)


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
        debug(f'Checking trigger for {self.name}')
        debug(f'Need to roll {(100 - self.getStatValue("chance"))} or higher to activate')
        debug(f'Rolled {rand}')
        if rand > 100 - self.getStatValue("chance"):
            debug("activated")
            self.applyBoost()

    """
    returns a text representation of this object
    """
    def getDisplayData(self) -> str:
        target = "user" if self.targetsUser else "that opponent"
        desc = [
            f'{self.name}:',
            entab(f'Whenever the user strikes an opponent, has a {self.getStatValue("chance")}% chance to inflict {target} with {self.getBoost().getDisplayData()}'),
        ]
        return "\n".join(desc)


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
        debug(f'Checking trigger for {self.name}')
        debug(f'Need to roll {(100 - self.getStatValue("chance"))} or higher to activate')
        debug(f'Rolled {rand}')
        if rand > 100 - self.getStatValue("chance"):
            debug("activated")
            self.applyBoost()

    """
    returns a text representation of this object
    """
    def getDisplayData(self) -> str:
        target = 'user' if self.targetsUser else 'the attacker'
        desc = [
            f'{self.name}:',
            entab(f'Whenever the user is struck by an opponent, has a {self.getStatValue("chance")}% chance to inflict {target} with {self.getBoost().getDisplayData()}')
        ]
        return "\n".join(desc)
