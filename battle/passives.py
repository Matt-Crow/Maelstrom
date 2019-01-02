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
        self.add_attr("status level", Stat("status level", status_level_form, 4)) #default to 20%
        self.add_attr("status duration", Stat("status duration", status_dur_form, 12)) #defaults to 3 turns


    def target_enemy(self):
        """
        Causes this' boosts to apply to the active enemy instead of the user
        """
        self.targets_user = False


    def set_boosted_stat(self, stat: str):
        """
        Temporary
        """
        self.boosted_stat = stat


    def set_lv(self, lv: int):
        """
        Also temp
        """
        self.set_base("status level", lv)


    def set_dur(self, dur: int):
        """
        Temp again
        """
        self.set_base("status duration", dur)


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
            target = self.user.team.enemy_team.active

        target.boost(self.get_boost())


    @staticmethod
    def read_save_code(code):
        ret = None

        #generate the name...
        name = ignore_text(code[0], "<PASSIVE>: ").strip()

        #boosts...
        boosts = []
        boost_codes = code[2:]
        for boost_code in boost_codes:
            boosts.append(Boost.read_save_code(boost_code))

        # and passive, can improve though
        if contains(code[1], "thresh:"):
            thresh = int(float(ignore_text(code[1], "thresh:")))
            ret = Threshhold(name, thresh, boosts)
        elif contains(code[1], "given:"):
            chance = int(float(ignore_text(code[1], "given:")))
            ret = OnHitGiven(name, chance, boosts)
        elif contains(code[1], "taken:"):
            chance = int(float(ignore_text(code[1], "taken:")))
            ret = OnHitTaken(name, chance, boosts)

        return ret


    @staticmethod
    def get_defaults() -> list:
        """
        Returns the default passives
        """
        p = Threshhold("Threshhold test", 10)
        p.set_boosted_stat("resistance")
        p.set_lv(20)
        p.set_dur(5)

        o = OnHitGiven("OnHitGivenTest", 10)
        o.set_boosted_stat("luck")
        o.set_lv(4)
        o.set_dur(20)

        h = OnHitTaken("OnHitTakenTest", 10)
        h.set_boosted_stat("control")
        h.set_lv(4)
        h.set_dur(5)
        h.target_enemy()

        return [p, o, h]




class Threshhold(AbstractPassive):
    """
    Automatically invoked at the end of every turn
    """
    def __init__(self, name, threshhold):
        super(self.__class__, self).__init__(name)
        self.set_type("Threshhold Passive")
        self.add_attr("threshhold", Stat("threshhold", thresh_form, threshhold))


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
    def __init__(self, name, chance):
        super(self.__class__, self).__init__(name)
        self.set_type('On Hit Given Passive')
        self.add_attr('chance', Stat('chance', chance_form, chance))


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
    def __init__(self, name, chance):
        super(self.__class__, self).__init__(name)
        self.set_type('On Hit Taken Passive')
        self.add_attr('chance', Stat('chance', chance_form, chance))


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
    return 0.05 * base


def status_dur_form(base: int) -> int:
    """
    Calculates the number of turns a status lasts
    """
    return 1 + int(float(base) / 5)


def thresh_form(base: int) -> float:
    """
    Calculates the HP threshhold that a passive
    should activate under (as a percentage)
    """
    return base * 0.05


def chance_form(base: int) -> int:
    """
    Calculates what the activation chance for this should be,
    from 0 to 100
    """
    return base * 5
