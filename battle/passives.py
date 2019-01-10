from utilities import *
from stat_classes import Stat, Boost

from upgradable import AbstractUpgradable

from output import Op


"""
Passives
"""
class AbstractPassive(AbstractUpgradable):
    """
    HOW TO ADD A PASSIVE TO A CHARACTER:
    1. define the passive:
    * pas = ~~~Passive(~ ~ ~ ~ ~ ~)
    2. append the passive:
    * character.passives.append(pas)
    3. set the user:
    * pas.set_user(character)
    """
    def __init__(self, name: str):
        super(AbstractPassive, self).__init__(name)
        self.set_type("Passive")

        self.boosted_stat = None
        self.targets_user = True

        self.track_attr('targets_user')
        self.track_attr('boosted_stat')
        self.add_attr("status level", Stat("status level", status_level_form, 4)) #default to 20%
        self.add_attr("status duration", Stat("status duration", status_dur_form, 12)) #defaults to 3 turns


    @staticmethod
    def read_json(json: dict) -> 'AbstractPassive':
        """
        Reads a JSON object as a dictionary, then converts it to a passive
        """
        #some way to auto-do this?
        name = json.get("name", "NAME NOT FOUND")
        ptype = json.get("type", "TYPE NOT FOUND")
        custom_points = int(json.get('customization_points', 0))
        targ = json.get('targets_user', True)

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

        ret.customization_points = custom_points
        ret.boosted_stat = json.get('boosted_stat', None)
        ret.targets_user = targ

        return ret


    def get_boost(self) -> 'Boost':
        """
        Returns the Boost this will inflict
        """
        boost = self.get_stat("status level")
        if not self.targets_user:
            boost = -boost

        return Boost(self.boosted_stat, boost, self.get_stat("status duration"), self.name)


    def f(self):
        """
        Applies this' boost
        """
        target = self.user

        if not self.targets_user:
            target = self.user.team.enemy.active

        target.boost(self.get_boost())


    @staticmethod
    def get_defaults() -> list:
        """
        Returns the default passives

        todo: make this read from a file
        """
        p = AbstractPassive.read_json({
            'name': 'Threshhold test',
            'type': 'Threshhold Passive',
            'boosted_stat' : 'resistance',
            'threshhold' : {
                'type' : 'Stat',
                'base' : 10,
                'name' : 'threshhold'
            },
            'status level' : {
                'type': 'Stat',
                'base': 5,
                'name': 'status level'
            },
            'status duration' : {
                'type': 'Stat',
                'base': 0,
                'name': 'status duration'
            },
            'targets_user' : 'True'
        })

        o = AbstractPassive.read_json({
            'name': 'On Hit Given Test',
            'type': 'On Hit Given Passive',
            'boosted_stat' : 'luck',
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
            'targets_user' : 'True'
        })

        h = AbstractPassive.read_json({
            'name': 'On Hit Taken Test',
            'type': 'On Hit Taken Passive',
            'boosted_stat' : 'control',
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
            'targets_user' : 'False'
        })

        return [p, o, h]




class Threshhold(AbstractPassive):
    """
    Automatically invoked at the end of every turn
    """
    def __init__(self, name):
        super(self.__class__, self).__init__(name)
        self.set_type("Threshhold Passive")
        self.add_attr("threshhold", Stat("threshhold", thresh_form, 4))


    def init_for_battle(self):
        self.user.add_on_update_action(self.check_trigger)


    def check_trigger(self):
        Dp.add("Checking trigger for " + self.name)
        Dp.add(str(self.get_stat("threshhold") * 100) + "% threshhold")
        Dp.add(str(self.user.hp_perc()) + "% user health")
        if self.user.hp_perc() <= self.get_stat("threshhold"):
            Dp.add("activated")
            self.f()
        Dp.dp()


    def get_data(self) -> list:
        """
        returns a text representation of this object
        """
        target = 'user' if self.targets_user else 'active enemy'
        return [
            self.name + ':',
            '\tInflicts ' + target + ' with a ' + str(self.get_stat('status level') * 100) + '% bonus',
            '\tto their ' + self.boosted_stat + ' stat',
            '\tfor ' + str(self.get_stat('status duration')) + ' turns',
            '\twhen the user is at or below ' + str(self.get_stat('threshhold') * 100) + '% of their maximum hit points.'
        ]


class OnHitGiven(AbstractPassive):
    def __init__(self, name):
        super(self.__class__, self).__init__(name)
        self.set_type('On Hit Given Passive')
        self.add_attr('chance', Stat('chance', chance_form, 4))


    def init_for_battle(self):
        self.user.add_on_hit_given_action(self.check_trigger)


    def check_trigger(self, onHitEvent):
        rand = roll_perc(self.user.get_stat("luck"))
        Dp.add("Checking trigger for " + self.name)
        Dp.add("Need to roll " + str(100 - self.get_stat('chance')) + " or higher to activate")
        Dp.add("Rolled " + str(rand))
        if rand > 100 - self.get_stat('chance'):
            Dp.add("activated")
            self.f()
        Dp.dp()


    def get_data(self) -> list:
        """
        returns a text representation of this object
        """
        target = 'user' if self.targets_user else 'that opponent'
        return [
            self.name + ':',
            '\tWhenever the user strikes an opponent, has a ' + str(self.get_stat('chance')) + '% chance to',
            '\tinflict ' + target + ' with a ' + str(self.get_stat('status level') * 100) + '% bonus',
            '\tto their ' + self.boosted_stat + ' stat',
            '\tfor ' + str(self.get_stat('status duration')) + ' turns'
        ]


class OnHitTaken(AbstractPassive):
    def __init__(self, name):
        super(self.__class__, self).__init__(name)
        self.set_type('On Hit Taken Passive')
        self.add_attr('chance', Stat('chance', chance_form, 4))


    def init_for_battle(self):
        self.user.add_on_hit_taken_action(self.check_trigger)


    def check_trigger(self, onHitEvent):
        rand = roll_perc(self.user.get_stat("luck"))
        Dp.add("Checking trigger for " + self.name)
        Dp.add("Need to roll " + str(100 - self.get_stat('chance')) + " or higher to activate")
        Dp.add("Rolled " + str(rand))
        if rand > 100 - self.get_stat('chance'):
            Dp.add("activated")
            self.f()
        Dp.dp()


    def get_data(self) -> list:
        """
        returns a text representation of this object
        """
        target = 'user' if self.targets_user else 'the attacker'
        return [
            self.name + ':',
            '\tWhenever the user is struck by an opponent, has a ' + str(self.get_stat('chance')) + '% chance to',
            '\tinflict ' + target + ' with a ' + str(self.get_stat('status level') * 100) + '% bonus',
            '\tto their ' + self.boosted_stat + ' stat',
            '\tfor ' + str(self.get_stat('status duration')) + ' turns'
        ]


def status_level_form(base: int) -> float:
    """
    Calculates the boost from statuses
    """
    return 0.2 + 0.025 * base


def status_dur_form(base: int) -> int:
    """
    Calculates the number of turns a status lasts
    """
    return 3 + int(float(base) / 5)


def thresh_form(base: int) -> float:
    """
    Calculates the HP threshhold that a passive
    should activate under (as a percentage)
    """
    return 0.2 + base * 0.025


def chance_form(base: int) -> int:
    """
    Calculates what the activation chance for this should be,
    from 0 to 100
    """
    return 20 + int(base * 2.5)
