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
