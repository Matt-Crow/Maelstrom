from utilities import *
from util.stringUtil import entab

"""
Stat stuff
"""

class Stat(object):
    """
    A class used to store
    information about a stat,
    making it easier to keep
    track of values
    """
    def __init__(self, name, formula, base: int, min_base = -10, max_base = 10, description = lambda base: f'base {base}'):
        """
        Creates a new stat.
        Forumula is a function that takes an integer as a parameter,
        and returns a float.

        base is a value between min_base and max_base,
        which is used to generate the stat's value when
        reading it as a string.

        min_base is the lowest base value this stat can have,
        and max_base functions similarly.

        TODO: add min max
        """
        self.name = name
        self.formula = formula
        self.boosts = []
        self.max_base = max_base
        self.min_base = min_base
        self.description = description

        self.set_base(base)
        self.value = None

    def calc(self):
        """
        Calulates what value this should have.

        Note that this does not return anything
        """
        self.value = self.formula(self.base)


    def is_max(self) -> bool:
        """
        Returns whether or not this' base
        is the maximum base allowed for this Stat
        """
        return self.base >= self.max_base


    def is_min(self) -> bool:
        """
        Returns whether or not this' base
        is the minimum base allowed for this Stat
        """
        return self.base <= self.min_base


    def boost(self, boost):
        self.boosts.append(boost)

    def get(self):
        mult = 1.0
        if self.value is None:
            self.calc()

        for boost in self.boosts:
            mult += boost.amount
        return self.value * mult

    def set_base(self, base: int):
        """
        Sets this' base to the given value
        """
        self.base = base

    def get_base(self) -> int:
        """
        Returns the value used to
        generate this stat
        """
        return self.base

    def reset_boosts(self):
        self.boosts = []

    def update(self):
        new_boosts = []
        for boost in self.boosts:
            """
            a stat boost with a duration
            of 1 will be checked, then
            down to 0, while a duration
            of -1 will always fail the
            check; thus, lasting forever
            """
            if boost.duration != 0:
                new_boosts.append(boost)
                boost.duration -= 1
        self.boosts = new_boosts

    def toString(self):
        return self.description(self.base)

    def displayData(self):
        Dp.add(self.name);
        Dp.add("Raw: " + str(self.base_value))
        Dp.add("Boosts:")
        for boost in self.boosts:
            boost.displayData()
        Dp.add("Calculated: " + str(self.value))
        Dp.dp()


class Boost(object):
    def __init__(self, stat_name, amount, duration, id = "NoIDSet"):
        self.stat_name = stat_name
        self.amount = amount
        if abs(self.amount) > 1.0:
            self.amount = float(self.amount) / 100
        self.base_duration = duration
        self.duration = duration
        self.id = id

    def reset(self):
        self.duration = self.base_duration

    def getDisplayData(self)->str:
        ret = f'+{int(self.amount * 100)}% {self.stat_name}'
        if self.duration > 0:
            ret += f' for {self.duration} turns'
        return ret

    """
    Returns a copy of this Boost
    """
    def copy(self)->"Boost":
        return Boost(self.stat_name, self.amount, self.base_duration, self.id)
