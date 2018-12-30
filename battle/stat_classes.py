from utilities import *

"""
Stat stuff
"""

#TODO: make this used like Orpheus stat, saving the base value
class Stat(object):
    """
    A class used to store
    information about a stat,
    making it easier to keep
    track of values
    """
    def __init__(self, name, formula, base: int, min_base = 0, max_base = 20):
        """
        Creates a new stat.
        Forumula is a function that takes an integer as a parameter,
        and returns a float.

        base is a value between min_base and max_base,
        which is used to generate the stat's value when
        reading it as a string.

        min_base is the lowest base value this stat can have,
        and max_base functions similarly.
        """
        self.name = name
        self.formula = formula
        self.base = base
        self.boosts = []
        self.value = 0

    def calc(self, level = 0):
        """
        Calulates what value this should have.
        level is usually the level of the user of this stat.
        i.e. if this is used for an attack, the user of the attack's
        level is passed in.

        Note that this does not return anything
        """
        self.value = self.formula(self.base) * (1 + 0.2 * level)

    def boost(self, boost):
        self.boosts.append(boost)

    def get(self):
        mult = 1.0
        for boost in self.boosts:
            mult += boost.amount
        return self.value * mult

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

    def display_data(self):
        Dp.add(self.name);
        Dp.add("Raw: " + str(self.base_value))
        Dp.add("Boosts:")
        for boost in self.boosts:
            boost.display_data()
        Dp.add("Calculated: " + str(self.value))
        Dp.dp()


#TODO: move this
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

    def get_data(self):
        ret = [
            "Boost: " + self.id,
            "\t+" + str(int(self.amount * 100)) + "% to",
            "\t" + self.stat_name + " stat"
        ]

        if self.duration > 0:
            ret.append("\tfor " + str(self.duration) + " turns")
        return ret

    def generate_save_code(self):
        """
        Returns a string that is
        used for save files
        """
        ret = "b " + self.id + "/"
        ret += self.stat_name + "/"
        ret += str(self.amount) + "/"
        ret += str(self.base_duration)
        return ret

    @staticmethod
    def read_save_code(code):
        code = code.split("/")
        id = ignore_text(code[0], "b").strip()
        stat = code[1].strip()
        amount = float(code[2])
        dur = int(float(code[3]))
        return Boost(stat, amount, dur, id)
