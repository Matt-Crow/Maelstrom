"""
This module contains the definitions for all the stats of active abilities
"""

from characters.stat_classes import Stat

class ActiveStatFactory(object):
    def makeDamageMultiplier(self, base: int):
        f = lambda base: 1.0 + base * 0.05
        return Stat(
            name = "damage multiplier",
            formula = f,
            base = base,
            description = lambda base: f'damage is multiplied by {f(base)}'
        )
