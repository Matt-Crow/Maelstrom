import random

from inputOutput.output import debug


ELEMENTS = ("lightning", "rain", "hail", "wind")
STATS = ("control", "resistance", "potency", "luck", "energy")

def roll_perc(base = 0):
    """
    Chooses a random number
    between base and 100,
    use
    roll_perc(self.getStatValue("luck"))
    """
    ret = 100
    base = int(base)
    # don't roll if base is more than 100
    if base > 100 or 0 > base:
        raise ValueError(f'base must be between 0 and 100, so {base} is not allowed')
    else:
        ret = random.randint(base, 100)
        debug(f'Rolling between {base} and 100')
        debug(f'Rolled {ret}')

    return ret
