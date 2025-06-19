# TODO fix these in #12 
# from maelstrom.dataClasses.activeAbilities import AbstractActive, TargetOption
# from maelstrom.dataClasses.team import Team

from maelstrom.characters.specification import CharacterSpecification
from maelstrom.characters.template import CharacterTemplate
from maelstrom.gameplay.events import ActionRegister, UPDATE_EVENT
from maelstrom.dataClasses.stat_classes import Stat
from maelstrom.util.stringUtil import entab, lengthOfLongest

_STATS = ["control", "resistance", "potency", "luck", "energy"]

class Character:
    """
    A Character is an entity within the game who has various stats and attributes.
    """

    team: "Team"
    
    ordinal: int
    """This Character's position on the Team. For example, 0 means they are in the first slot."""

    def __init__(self, template: CharacterTemplate, specification: CharacterSpecification, actives: 'list[AbstractActive]'):
        self.name = template.name
        self.element = template.element

        # might run into issues with discrepencies between these two...
        # ... unless I store the level and the xp towards the next level?
        self.level = specification.level
        self.xp = specification.xp

        self.actives = actives
        
        self.stats = {}
        def _set_stat(name, offset):
            self.stats[name.lower()] = Stat(name, 20 + offset)
        _set_stat("control", template.control)
        _set_stat("resistance", template.resistance)
        _set_stat("energy", template.energy)
        _set_stat("potency", template.potency)
        _set_stat("luck", template.luck)
        self._calc_stats()

        max_energy = int(self.get_stat_value("energy"))
        self._health_pool = Pool(100, 100)
        self._energy_pool = Pool(int(max_energy / 2), max_energy)
        
        self._event_listeners = ActionRegister()

    @property
    def remaining_hp(self) -> int:
        return self._health_pool.value

    @property
    def energy(self) -> int:
        return self._energy_pool.value

    def to_specification(self) -> CharacterSpecification:
        """
        Returns a specification from which this Character can be reconstructed.
        """
        spec = CharacterSpecification(
            name=self.name,
            level=self.level,
            xp=self.xp,
            active_names=[active.name for active in self.actives]
        )
        return spec

    def init_for_battle(self):
        """
        Resets everything for the upcoming battle
        """

        self._event_listeners.clear()
        self._calc_stats()

        # don't need to do anything with actives

        self._health_pool.reset()
        self._energy_pool.reset()

    def _calc_stats(self):
        """
        Calculates all this' stats
        """
        for stat in self.stats.values():
            stat.reset_boosts()

    def get_stat_value(self, statName: str) -> float:
        return self.stats[statName.lower()].get()

    def add_event_listener(self, enum_type, action):
        self._event_listeners.add_event_listener(enum_type, action)

    def fire_event_listeners(self, enum_type, event=None):
        self._event_listeners.fire(enum_type, event)

    def get_percent_hp_remaining(self):
        """
        Returns as a value between 0 and 100
        """
        return int((float(self._health_pool.value) / float(self._health_pool.max) * 100.0))

    def get_display_data(self) -> str:
        self._calc_stats()
        ret = [
            f'{self.name} Lv. {self.level} {self.element}',
            entab(f'{self.xp} / {self.level * 10} XP')
        ]

        ret.append("STATS:")
        width = lengthOfLongest(_STATS)
        for stat in _STATS:
            ret.append(entab(f'{stat.ljust(width)}: {int(self.get_stat_value(stat))}'))

        ret.append("ACTIVES:")
        for active in self.actives:
            ret.append(f'* {active.description}')

        return "\n".join(ret)

    """
    Battle functions:
    Used during battle
    """

    def get_target_options(self)->'list[TargetOption]':
        """
        use this to find out which enemies this Character can target and with
        which abilities
        """
        useable_actives = [active for active in self.actives if active.canUse(self)]
        choices = []
        for active in useable_actives:
            choices.extend(active.get_target_options(self))
        return choices

    def boost(self, boost):
        """
        Increase or lower stats in battle. Returns the boost this receives with its
        potency stat factored in
        """
        mult = 1 + self.get_stat_value("potency") / 100
        boost = boost.copy()
        boost.amount *= mult
        self.stats[boost.stat_name].add_boost(boost)
        return boost

    def heal_percent(self, percent):
        """
        Restores HP. Converts an INTEGER to a percentage. Returns the amount of HP
        healed.
        """
        return self.heal_amount(int(self._health_pool.max * (float(percent) / 100))) 
    
    def heal_amount(self, amount: int) -> int:
        """Returns actual amount of HP healed."""
        mult = 1 + self.get_stat_value("potency") / 100
        healing = int(mult * amount)
        self._health_pool.add(int(healing))
        return healing

    def harm(self, percent):
        """
        returns the actual amount of damage inflicted
        """
        mult = 1 - self.get_stat_value("potency") / 100
        harming = self._health_pool.max * (float(percent) / 100)
        amount = int(harming * mult)
        self.take_damage(amount)
        return amount

    def take_damage(self, dmg):
        self._health_pool.subtract(int(dmg))

    def gain_energy(self, amount) -> int:
        """
        Returns the amount of energy gained
        """
        mult = 1 + self.get_stat_value("potency") / 100
        amount = int(amount * mult)
        self._energy_pool.add(amount)
        return amount

    def lose_energy(self, amount):
        self._energy_pool.subtract(int(amount))

    def update(self):
        self.fire_event_listeners(UPDATE_EVENT, self)
        self.gain_energy(self.get_stat_value("energy") * 0.15)
        for stat in self.stats.values():
            stat.update()

    def is_koed(self):
        return self._health_pool.value <= 0

    def gain_xp(self, amount)->list[str]:
        """
        Give experience, possibly leveling up this character.

        Returns a list of messages to display, if any.
        """
        msgs = []
        self.xp += amount
        while self.xp >= self.level * 10:
            msgs.append(f'{self.name} leveled up!')
            self.xp -= self.level * 10
            self.level += 1
            self._calc_stats()
            self._health_pool.reset()
            msgs.append(self.get_display_data())
        self.xp = int(self.xp)
        return msgs

    def __str__(self):
        return self.name

class Pool:
    """A pool of either hit points or energy"""

    def __init__(self, value: int, max: int) -> None:
        self._start = value
        self._value = value
        self._max = max
    
    @property
    def value(self) -> int:
        return self._value
    
    @property
    def max(self) -> int:
        return self._max
    
    def add(self, amount: int):
        self._value += amount
        if self._value > self._max:
            self._value = self._max

    def subtract(self, amount: int):
        self._value -= amount
        if self._value < 0:
            self._value = 0
    
    def reset(self):
        self._value = self._start