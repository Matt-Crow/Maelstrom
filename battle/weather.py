import random
from utilities import Op
from stat_classes import Boost

class Weather(object):
    """
    This is what makes Maelstrom unique!
    Weather provides in-battle effects
    that alter the stats of characters
    """

    types = {
        "lightning": "The sky rains down its fire upon the field...",
        "rain": "A deluge of water pours forth from the sky...",
        "hail": "A light snow was falling...",
        "wind": "The strong winds blow mightily...",
        None: "The land is seized by an undying calm..."
    }

    def __init__(self, type, intensity):
        """
        The type determines what sort of effect will
        be applied to all participants in a battle.
        The intensity is how potent the effect will be.
        The msg is what text will show to help
        the player determine the weather.
        """
        self.intensity = intensity

        if type in Weather.types:
            self.type = type
        else:
            self.type = Weather.random_type()

        self.msg = Weather.types[type]

    def do_effect(self, affected):
        """
        Apply stat changes
        to a team
        """
        if self.type == "lightning":
            for person in affected:
                person.gain_energy(self.intensity)

        if self.type == "wind":
            for person in affected:
                person.boost(Boost("control", self.intensity * 5, 1, "Weather"))

        if self.type == "hail":
            for person in affected:
                person.harm(self.intensity * 4)

        if self.type == "rain":
            for person in affected:
                person.heal(self.intensity * 3)

    def disp_msg(self):
        """
        Print a message showing
        the weather condition
        """
        Op.add(self.msg)
        Op.dp()

    @staticmethod
    def generate_random():
        return Weather(Weather.random_type(), Weather.random_intensity())

    @staticmethod
    def random_type():
        return random.choice(list(Weather.types.keys()))

    @staticmethod
    def random_intensity():
        return random.randint(1, 5)
