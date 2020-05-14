from utilities import *
from stat_classes import Stat, Boost

from customizable import AbstractCustomizable

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

    @staticmethod
    def loadJson(jdict: dict)->"AbstractPassive":
        ret = None
        type = jdict["type"]
        if type == "Threshhold Passive":
            ret = Threshhold(**jdict)
        elif type == "On Hit Given Passive":
            ret = OnHitGiven(**jdict)
        elif type == "On Hit Taken Passive":
            ret = OnHitTaken(**jdict)
        else:
            raise Exception("Type not found for AbstractActive: " + type)
        return ret

    @staticmethod # get rid of this
    def read_json(json: dict) -> 'AbstractPassive':
        """
        Reads a JSON object as a dictionary, then converts it to a passive
        """
        #some way to auto-do this?
        name = json.get("name", "NAME NOT FOUND")
        ptype = json.get("type", "TYPE NOT FOUND")
        custom_points = int(json.get('customPoints', 0))
        targ = json.get('targetsUser', True)

        ret = None

        if ptype == 'Threshhold Passive':
            ret = Threshhold(name)
            ret.set_base('threshhold', int(json.get('threshhold', {'base':4}).get('base', 4)))
        elif ptype == 'On Hit Given Passive':
            ret = OnHitGiven(name)
            ret.set_base('chance', int(json.get('chance', {'base':4}).get('base', 4)))
        elif ptype == 'On Hit Taken Passive':
            ret = OnHitTaken(name)
            ret.set_base('chance', int(json.get('chance', {'base':4}).get('base', 4)))
        else:
            raise Exception('Type not found for AbstractActive: ' + ptype)


        for k, v in json.items():
            if type(v) == type({}) and v.get('type', 'NO TYPE') == 'Stat':
                ret.set_base(k, int(v.get('base', 0)))

        ret.customPoints = custom_points
        ret.boostedStat = json.get('boostedStat', None)
        ret.targetsUser = targ

        return ret

    """
    Returns the Boost this will inflict
    """
    def getBoost(self)->"Boost":
        lv = self.getStatValue("status level")
        if not self.targetsUser:
            lv = -lv

        return Boost(self.boostedStat, boost, self.getStatValue("status duration"), self.name)

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
            stats={
                "threshhold" : 10,
                "status level" : 0,
                "status duration" : -10
            }
        )
        Op.add(p.getDisplayData())
        Op.display()

        o = AbstractPassive.read_json({
            'name': 'On Hit Given Test',
            'type': 'On Hit Given Passive',
            'boostedStat' : 'luck',
            'chance' : {
                'type': 'Stat',
                'base': 5,
                'name': 'chance'
            },
            'status level' : {
                'type': 'Stat',
                'base': 0,
                'name': 'status level'
            },
            'status duration' : {
                'type': 'Stat',
                'base': 10,
                'name': 'status duration'
            },
            'targetsUser' : 'True'
        })

        h = AbstractPassive.read_json({
            'name': 'On Hit Taken Test',
            'type': 'On Hit Taken Passive',
            'boostedStat' : 'control',
            'chance' : {
                'type': 'Stat',
                'base': 0,
                'name': 'chance'
            },
            'status level' : {
                'type': 'Stat',
                'base': 10,
                'name': 'status level'
            },
            'status duration' : {
                'type': 'Stat',
                'base': 5,
                'name': 'status duration'
            },
            'targetsUser' : 'False'
        })

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
        self.user.add_on_update_action(self.checkTrigger)


    def checkTrigger(self):
        Dp.add("Checking trigger for " + self.name)
        Dp.add(str(self.get_stat("threshhold") * 100) + "% threshhold")
        Dp.add(str(self.user.getHpPerc()) + "% user health")
        if self.user.getHpPerc() <= self.getStatValue("threshhold"):
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
    def __init__(self, name):
        super(self.__class__, self).__init__(name)
        self.set_type('On Hit Given Passive')
        self.add_attr('chance', Stat('chance', chance_form, 4))


    def initForBattle(self):
        self.user.add_on_hit_given_action(self.checkTrigger)


    def checkTrigger(self, onHitEvent):
        rand = roll_perc(self.user.get_stat("luck"))
        Dp.add("Checking trigger for " + self.name)
        Dp.add("Need to roll " + str(100 - self.get_stat('chance')) + " or higher to activate")
        Dp.add("Rolled " + str(rand))
        if rand > 100 - self.get_stat('chance'):
            Dp.add("activated")
            self.applyBoost()
        Dp.dp()


    def getDisplayData(self) -> list:
        """
        returns a text representation of this object
        """
        target = 'user' if self.targetsUser else 'that opponent'
        return [
            self.name + ':',
            '\tWhenever the user strikes an opponent, has a ' + str(self.get_stat('chance')) + '% chance to',
            '\tinflict ' + target + ' with a ' + str(self.get_stat('status level') * 100) + '% bonus',
            '\tto their ' + self.boostedStat + ' stat',
            '\tfor ' + str(self.get_stat('status duration')) + ' turns'
        ]


class OnHitTaken(AbstractPassive):
    def __init__(self, name):
        super(self.__class__, self).__init__(name)
        self.set_type('On Hit Taken Passive')
        self.add_attr('chance', Stat('chance', chance_form, 4))


    def initForBattle(self):
        self.user.add_on_hit_taken_action(self.checkTrigger)


    def checkTrigger(self, onHitEvent):
        rand = roll_perc(self.user.get_stat("luck"))
        Dp.add("Checking trigger for " + self.name)
        Dp.add("Need to roll " + str(100 - self.get_stat('chance')) + " or higher to activate")
        Dp.add("Rolled " + str(rand))
        if rand > 100 - self.get_stat('chance'):
            Dp.add("activated")
            self.applyBoost()
        Dp.dp()


    def getDisplayData(self) -> list:
        """
        returns a text representation of this object
        """
        target = 'user' if self.targetsUser else 'the attacker'
        return [
            self.name + ':',
            '\tWhenever the user is struck by an opponent, has a ' + str(self.get_stat('chance')) + '% chance to',
            '\tinflict ' + target + ' with a ' + str(self.get_stat('status level') * 100) + '% bonus',
            '\tto their ' + self.boostedStat + ' stat',
            '\tfor ' + str(self.get_stat('status duration')) + ' turns'
        ]




def chance_form(base: int) -> int:
    """
    Calculates what the activation chance for this should be,
    from 0 to 100
    """
    return 20 + int(base * 2.5)
