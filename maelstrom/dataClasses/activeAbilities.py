"""
Active abilities are attributes a character can have that they ACTIVEly choose
to trigger on their turn.

Keep in mind that, in battle, when a Character needs to choose their active,
there are two components to consider:
1. what active do I want to use?
2. who do I want to hit with that active?
Characters make a choice of which TargetOption they wish to use, not just which
active they wish to use.
"""

from maelstrom.dataClasses.character import Character
from maelstrom.gameplay.events import OnHitEvent, HIT_GIVEN_EVENT, HIT_TAKEN_EVENT
from maelstrom.util.random import rollPercentage
from maelstrom.dataClasses.elements import ELEMENTS
from abc import abstractmethod
import functools

_MISS_CHANCE = 0.2
_MISS_MULTIPLIER = 0.75
_CRITICAL_HIT_CHANCE = 0.2
_CRITICAL_HIT_MULTIPLIER = 1.5

def _damage_at_level(level) -> int:
    """
    Returns base damage for a given level.
    For example, a level 1 character will deal about 17% damage,
    while a level 20 character will deal about 33% damage.
    This makes damage scale up over time.
    """
    return int(16.67 * (1 + float(level) * 0.05))


class TargetOption:
    """
    a TargetOption specifies who a user could potentially target using an active
    ability. For example, a melee attack allows a user to strike at a closeby
    enemy, while a ranged attack can target distant enemies

    Command design pattern
    """

    def __init__(self, active: "AbstractActive", user: Character, targets: list[Character]):
        self.active = active
        self.user = user
        self.targets = targets
        self._as_str = f'{active.name} -> {", ".join([target.name for target in targets])}'

        damages = [active.calcDamageAgainst(user, target) for target in targets]
        self._total_damage = functools.reduce(lambda total, next: total + next, damages)

    @property
    def total_damage(self) -> int:
        """Total damage this is expected to inflict."""
        return self._total_damage

    def __str__(self) -> str:
        return self._as_str

    def use(self) -> list[str]:
        """Uses this TargetOption and returns messages to display."""
        self.user.lose_energy(self.active.cost) # don't call this for each target
        return [self.active.resolveAgainst(self.user, target) for target in self.targets]
    

class AbstractActive:
    def __init__(self, name, description, cost):
        """
        name should be a unique identifier
        """
        self.name = name
        self.description = f'{name}: {description}'
        self.cost = cost

    @abstractmethod
    def copy(self) -> 'AbstractActive':
        pass

    @abstractmethod
    def calcDamageAgainst(self, user: Character, target: Character) -> int:
        """Calculates damage this would inflict, assuming no miss or crit"""
        pass

    @abstractmethod
    def resolveAgainst(self, user: Character, target: Character) -> str:
        """Resolves this attack, then returns the message to display in the UI"""
        pass

    def canUse(self, user: "Character")->bool:
        return self.cost <= user.energy and len(self.getTargetOptions(user)) > 0

    def getTargetOptions(self, user: "Character")->list[TargetOption]:
        """
        don't override this one
        """
        if len(user.team.enemyTeam.getMembersRemaining()) == 0:
            return []
        return [TargetOption(self, user, targets) for targets in self.doGetTargetOptions(user)]

    @abstractmethod
    def doGetTargetOptions(self, user: "Character")->list[list[Character]]:
        """
        subclasses must override this option to return the enemies this could
        potentially hit. Each element of the returned list represents a choice
        the user or AI can make, with each of those elements containing the
        enemies that attack would hit.
        """
        pass

class AbstractDamagingActive(AbstractActive):
    # not sure if I like so many paramters
    def __init__(self, name, description, cost, damageMult):
        super().__init__(name, description, cost)
        self.damageMult = damageMult

    def resolveAgainst(self, user: Character, target: Character) -> str:
        base_dmg = self.calcDamageAgainst(user, target)

        # check for miss, hit, or crit (mhc)
        rng = rollPercentage(int(user.get_stat_value("luck"))) / 100
        hit_multiplier = 1.0
        hit_message = "" # don't put a space at the end here
        if rng <= _MISS_CHANCE:
            hit_multiplier = _MISS_MULTIPLIER
            hit_message = "A glancing blow! " # need space at the end here
        elif rng >= 1.0 - _CRITICAL_HIT_CHANCE:
            hit_multiplier = _CRITICAL_HIT_MULTIPLIER
            hit_message = "A critical hit! " # need space at the end here
        
        dmg = int(base_dmg * hit_multiplier)
        event = OnHitEvent("Attack", user, target, self, dmg)
        target.take_damage(dmg)
        target.fire_event_listeners(HIT_TAKEN_EVENT, event)
        user.fire_event_listeners(HIT_GIVEN_EVENT, event)

        return f'{hit_message}{user.name} struck {target.name} for {dmg} damage using {self.name}!'

    def calcDamageAgainst(self, user: Character, target: Character) -> int:
        return int(_damage_at_level(user.level) * self.damageMult * user.get_stat_value("control") / target.get_stat_value("resistance"))

class MeleeActive(AbstractDamagingActive):
    def __init__(self, name, description, damageMult):
        super().__init__(name, description, 0, damageMult)
        self.damageMult = damageMult

    def copy(self):
        return MeleeActive(
            self.name,
            self.description,
            self.damageMult
        )

    def doGetTargetOptions(self, user: "Character")->list[list[Character]]:
        """
        MeleeActives can hit a single active target
        """
        return [[option] for option in getActiveTargets(user.ordinal, user.team.enemyTeam.getMembersRemaining())]

class ElementalActive(AbstractDamagingActive):
    def __init__(self, name):
        super().__init__(
            name,
            'strike an enemy for 1.75X damage',
            10,
            1.75
        )

    def copy(self):
        return ElementalActive(self.name)

    def doGetTargetOptions(self, user: "Character")->list[list[Character]]:
        """
        ElementalActives can hit a single cleave target
        """
        return [[option] for option in getCleaveTargets(user.ordinal, user.team.enemyTeam.getMembersRemaining())]



"""
Use these to decide which enemies to target. Should only allow user to choose
attacks that can hit anyone
"""


def getActiveTargets[T](attackerOrdinal: int, targetTeam: list[T]) -> list[T]:
    """
    'active' enemies are those across from the attacker and the enemy
    immediately below that. This gives a slight advantage to the 1 in a 1 vs 2,
    as both enemies cannot attack them at the same time

    O X
      X
    """
    options = []
    if attackerOrdinal < len(targetTeam):
        options.append(targetTeam[attackerOrdinal])
    if attackerOrdinal + 1 < len(targetTeam):
        options.append(targetTeam[attackerOrdinal + 1])
    return options

def getCleaveTargets[T](attackerOrdinal: int, targetTeam: list[T]) -> list[T]:
    """
    enemies are 'cleaveable' (for want of a better word) if they are no more
    than 1 array slot away from the enemy across from the attacker
      X
    O X
      X
    """
    options = getActiveTargets(attackerOrdinal, targetTeam)
    if attackerOrdinal - 1 >= 0 and attackerOrdinal - 1 < len(targetTeam):
        m = targetTeam[attackerOrdinal - 1]
        options.insert(0, m)
    return options

def getUniversalActives()->list[AbstractActive]:
    return [
        MeleeActive("slash", "strike a nearby enemy", 1.0)
    ]

def getActivesForElement(element)->list[AbstractActive]:
    return [ElementalActive(f'{element} bolt')]

def getActiveAbilityList()->list[AbstractActive]:
    options = getUniversalActives()
    for element in ELEMENTS:
        options.extend(getActivesForElement(element))
    options.extend(getActivesForElement("stone"))
    return options

def createDefaultActives(element)->list[AbstractActive]:
    options = getUniversalActives()
    options.extend(getActivesForElement(element))
    return [option.copy() for option in options]