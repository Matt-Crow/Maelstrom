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
from maelstrom.dataClasses.stat_classes import Boost
from maelstrom.gameplay.events import OnHitEvent
from maelstrom.util.random import rollPercentage
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

        damages = [active.get_damage_against(user, target) for target in targets]
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
        return [self.active.resolve_against(self.user, target) for target in self.targets]

_SELF = [
    0
]
_ADJACENT = [
    0, # across
    1, # below
]

_CLEAVE = [
    -1, # above
    0, # across
    1 # below
]

def in_bounds(enemy_ordinals: list[int], enemy_team_size: int) -> list[int]:
    return [number for number in enemy_ordinals if number >= 0 and number < enemy_team_size]


class AbstractActive:
    """Subclasses should be immutable."""

    def __init__(self, name: str, description: str, cost: int, targets_enemy_team: bool, target_offsets: list[int]):
        """
        name should be a unique identifier
        """
        self._name = name
        self._description = f'{name}: {description}'
        self._cost = cost
        self._targets_enemy_team = targets_enemy_team
        self._target_offsets = target_offsets

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def cost(self) -> int:
        return self._cost

    @abstractmethod
    def get_damage_against(self, user: Character, target: Character) -> int:
        """Calculates damage this would inflict, assuming no miss or crit"""
        pass

    @abstractmethod
    def resolve_against(self, user: Character, target: Character) -> str:
        """Resolves this attack, then returns the message to display in the UI"""
        pass

    def canUse(self, user: "Character")->bool:
        return self.cost <= user.energy and len(self.get_target_options(user)) > 0

    def get_target_options(self, user: "Character")->list[TargetOption]:
        
        target_team = user.team.enemyTeam if self._targets_enemy_team else user.team
        possible_targets = target_team.members_remaining

        possible_target_ordinals = [user.ordinal + offset for offset in self._target_offsets]
        actual_target_ordinals = in_bounds(possible_target_ordinals, len(possible_targets))
        actual_targets = [possible_targets[ordinal] for ordinal in actual_target_ordinals]

        # [option] to show only hitting one target per list of targets        
        lists_of_targets = [[target] for target in actual_targets]

        return [TargetOption(self, user, targets) for targets in lists_of_targets]


class DamagingActive(AbstractActive):
    def __init__(self, name: str, description: str, cost: int, target_offsets: list[int], damage_multiplier: float):
        super().__init__(name, description, cost, True, target_offsets)
        self._damage_multiplier = damage_multiplier

    def resolve_against(self, user: Character, target: Character) -> str:
        base_dmg = self.get_damage_against(user, target)

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
        target.event_hit_taken.publish_event(event)
        user.event_hit_given.publish_event(event)

        return f'{hit_message}{user.name} struck {target.name} for {dmg} damage using {self.name}!'

    def get_damage_against(self, user: Character, target: Character) -> int:
        return int(_damage_at_level(user.level) * self._damage_multiplier * user.get_stat_value("control") / target.get_stat_value("resistance"))

class BlockActive(AbstractActive):
    def __init__(self):
        super().__init__(
            "Block",
            "reduce damage taken and empower next hit",
            5,
            False,
            _SELF
        )
    
    def get_damage_against(self, user: Character, target: Character) -> int:
        return 0

    def resolve_against(self, user: Character, target: Character) -> str:
        target.boost(Boost("control", 0.5, 1))
        target.boost(Boost("resistance", 0.5, 1))
        return f"{target.name} is blocking and ready to strike back!"

class RestActive(AbstractActive):
    def __init__(self):
        super().__init__(
            "Rest", 
            "heal and restore energy", 
            0, 
            False,
            _SELF
        )
    
    def get_damage_against(self, user: Character, target: Character) -> int:
        return 0

    def resolve_against(self, user: Character, target: Character) -> str:
        amount_to_heal = int(0.8 * _damage_at_level(user.level))
        amount_to_restore = 8

        actual_heal = target.heal_amount(amount_to_heal)
        actual_restore = target.gain_energy(amount_to_restore)

        return f"{target.name} healed {actual_heal} and restored {actual_restore}!"

_DEFAULT_ACTIVES = [
    DamagingActive("slash", "strike a nearby enemy", 0, _ADJACENT, 1.0),
    BlockActive(),
    RestActive()
]

def _make_elemental_bolt(element) -> DamagingActive:
    return DamagingActive(f'{element} bolt', "strike an enemy for 1.75X damage", 10, _CLEAVE, 1.75)

ELEMENTS = ("lightning", "rain", "hail", "wind")

def get_all_actives() -> list[AbstractActive]:
    options = []
    options.extend(_DEFAULT_ACTIVES)
    for element in ELEMENTS:
        options.append(_make_elemental_bolt(element))
    options.append(_make_elemental_bolt("stone"))
    return options

def createDefaultActives(element)->list[AbstractActive]:
    options = []
    options.extend(_DEFAULT_ACTIVES)
    options.append(_make_elemental_bolt(element))
    return options