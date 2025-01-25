# TODO fix this in #12 
# from maelstrom.dataClasses.activeAbilities import TargetOption
from maelstrom.gameplay.events import ActionRegister, UPDATE_EVENT
from maelstrom.dataClasses.stat_classes import Stat
from maelstrom.util.serialize import AbstractJsonSerialable
from maelstrom.util.stringUtil import entab, lengthOfLongest

_STATS = ("control", "resistance", "potency", "luck", "energy")

class Character(AbstractJsonSerialable):
    """
    A Character is an entity within the game who has various stats and attributes.
    """

    def __init__(self, **kwargs):
        """
        required kwargs:
        - name : str
        - element : str
        - level : int (defaults to 1)
        - xp : int (defaults to 0)
        - actives : list of AbstractActives. Throws an error if not set
        - stats: object{ str : int } (defaults to 0 for each stat in STATS not given in the object)
        """

        super().__init__(**dict(kwargs, type="Character"))
        self.name = kwargs["name"]

        self._max_hp = 100

        # don't prefix with underscore - breaks JSON!
        self.element = kwargs["element"]
        self.level = kwargs.get("level", 1)
        self.xp = int(kwargs.get("xp", 0))
        self.actives = [active for active in kwargs["actives"]]
        self.stats = {}
        for stat in _STATS:
            self._add_stat(Stat(stat, lambda base: 20.0 + float(base), kwargs.get("stats", {}).get(stat, 0)))
        self._calc_stats()
        self.remaining_hp = self._max_hp

        self._event_listeners = ActionRegister()

        self.addSerializedAttributes(
            "name",
            "element", # todo rm once I use templates for #6
            "xp",
            "level",
            "actives",
            "stats"
        )

    def _add_stat(self, stat):
        self.stats[stat.name.lower()] = stat

    def init_for_battle(self):
        """
        Resets everything for the upcoming battle
        """

        self._event_listeners.clear()
        self._calc_stats()

        # don't need to do anything with actives

        self.remaining_hp = self._max_hp
        self.energy = int(self.get_stat_value("energy") / 2.0)

    def _calc_stats(self):
        """
        Calculates all this' stats
        """
        for stat in self.stats.values():
            stat.reset_boosts()
            stat.calc()

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
        return int((float(self.remaining_hp) / float(self._max_hp) * 100.0))

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
            choices.extend(active.getTargetOptions(self))
        return choices

    # TODO add ID checking to prevent doubling up
    def boost(self, boost):
        """
        Increase or lower stats in battle. Returns the boost this receives with its
        potency stat factored in
        """
        mult = 1 + self.get_stat_value("potency") / 100
        boost = boost.copy()
        boost.amount *= mult
        self.stats[boost.stat_name].boost(boost)
        return boost

    def heal(self, percent):
        """
        Restores HP. Converts an INTEGER to a percentage. Returns the amount of HP
        healed.
        """
        mult = 1 + self.get_stat_value("potency") / 100
        healing = self._max_hp * (float(percent) / 100) * mult
        self.remaining_hp = int(self.remaining_hp + healing)

        if self.remaining_hp > self._max_hp:
            self.remaining_hp = self._max_hp

        return int(healing)

    def harm(self, percent):
        """
        returns the actual amount of damage inflicted
        """
        mult = 1 - self.get_stat_value("potency") / 100
        harming = self._max_hp * (float(percent) / 100)
        amount = int(harming * mult)
        self.take_damage(amount)
        return amount

    def take_damage(self, dmg):
        self.remaining_hp -= dmg
        self.remaining_hp = int(self.remaining_hp)
        return dmg

    def gain_energy(self, amount):
        """
        Returns the amount of energy gained
        """
        mult = 1 + self.get_stat_value("potency") / 100
        amount = int(amount * mult)
        self.energy += amount

        if self.energy > self.get_stat_value("energy"):
            self.energy = self.get_stat_value("energy")

        self.energy = int(self.energy)

        return amount

    def lose_energy(self, amount):
        self.energy -= amount
        if self.energy < 0:
            self.energy = 0

    def update(self):
        self.fire_event_listeners(UPDATE_EVENT, self)
        self.gain_energy(self.get_stat_value("energy") * 0.15)
        for stat in self.stats.values():
            stat.update()

    def is_koed(self):
        return self.remaining_hp <= 0

    """
    Post-battle actions:
    Occur after battle
    """

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
            self.remaining_hp = self._max_hp
            msgs.append(self.get_display_data())
        self.xp = int(self.xp)
        return msgs

    def __str__(self):
        return self.name