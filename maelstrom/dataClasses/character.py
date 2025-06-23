# TODO fix these in #12 
# from maelstrom.dataClasses.activeAbilities import AbstractActive, TargetOption
# from maelstrom.dataClasses.team import Team

from maelstrom.characters.specification import CharacterSpecification
from maelstrom.characters.template import CharacterTemplate
from maelstrom.gameplay.events import EventPublisher, OnHitEvent
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
        def _set_stat(stat_name, stars):
            if stars < 1 or stars > 5:
                raise ValueError(f"{template.name} {stat_name} = {stars}, which is outside the allowed range of 1-5")
            self.stats[stat_name.lower()] = Stat(stat_name, 5 + 5 * stars)
        _set_stat("control", template.control)
        _set_stat("resistance", template.resistance)
        _set_stat("energy", template.energy)
        _set_stat("potency", template.potency)
        _set_stat("luck", template.luck)
        self._calc_stats()

        max_energy = int(self.get_stat_value("energy"))
        self._health_pool = Pool(100, 100)
        self._energy_pool = Pool(int(max_energy / 2), max_energy)
        
        self._event_update = EventPublisher()
        self._event_hit_taken = EventPublisher()
        self._event_hit_given = EventPublisher()

    @property
    def remaining_hp(self) -> int:
        return self._health_pool.value

    @property
    def energy(self) -> int:
        return self._energy_pool.value
    
    @property
    def event_update(self) -> "EventPublisher[Character]":
        return self._event_update
    
    @property
    def event_hit_taken(self) -> EventPublisher[OnHitEvent]:
        return self._event_hit_taken
    
    @property
    def event_hit_given(self) -> EventPublisher[OnHitEvent]:
        return self._event_hit_given

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

        self._event_update.clear_subscribers()
        self._event_hit_taken.clear_subscribers()
        self._event_hit_given.clear_subscribers()
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
        self._event_update.publish_event(self)
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


class Stat:
    """
    A class used to store
    information about a stat,
    making it easier to keep
    track of values
    """

    def __init__(self, name, value: int):
        self._name = name
        self._boosts = []
        self._value = value

    @property
    def name(self) -> str:
        return self._name
    
    def add_boost(self, boost):
        self._boosts.append(boost)

    def get(self) -> float:
        mult = 1.0 + sum([b.amount for b in self._boosts])
        return self._value * mult

    def reset_boosts(self):
        self._boosts = []

    def update(self):
        # duration 1 is kept, ticks down to 0, then is discarded next time
        # duration < 0, like -1, means keep forever
        self._boosts = [b for b in self._boosts if b.duration != 0]
        for boost in self._boosts:
            boost.duration -= 1


class Boost:
    def __init__(self, stat_name: str, amount: float, duration: int):
        self.stat_name = stat_name
        self.amount = amount
        self.base_duration = duration
        self.duration = duration

    def get_boost_text(self)->str:
        ret = f'+{int(self.amount * 100)}% {self.stat_name}'
        if self.duration > 0:
            ret += f' for {self.duration} turns'
        return ret

    def copy(self) -> "Boost":
        """Needed because Boosts are mutable"""
        return Boost(self.stat_name, self.amount, self.base_duration)