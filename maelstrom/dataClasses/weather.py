from maelstrom.dataClasses.character import Boost, Character
import abc



class Weather:
    """
    This is what gives Maelstrom its name. Weather provides in-battle effects that
    alter the stats of characters. This is an abstract class
    """

    def __init__(self, name: str, msg: str):
        self.name = name
        self.msg = msg

    def getMsg(self):
        return self.msg

    def applyEffect(self, affected: list[Character], msgs: list[str]):
        """
        Apply stat changes to a list of Characters. Appends messages to the
        given list of messages based on how it effects them
        """
        for person in affected:
            msgs.append(self.doApplyEffect(person))

    @abc.abstractmethod
    def doApplyEffect(self, target: "Character")->str:
        pass

class Lightning(Weather):
    def __init__(self):
        super().__init__("lightning", "The sky rains down its fire upon the field...")

    def doApplyEffect(self, target: "Character")->str:
        amount = target.gain_energy(3)
        return f'The charged atmosphere provides {target.name} with {amount} energy'

class Rain(Weather):
    def __init__(self):
        super().__init__("rain", "A deluge of water pours forth from the sky...")

    def doApplyEffect(self, target: "Character")->str:
        amount = target.heal_percent(9)
        return f'The restorative rain heals {target.name} by {amount} HP'

class Hail(Weather):
    def __init__(self):
        super().__init__("hail", "A light snow was falling...")

    def doApplyEffect(self, target: "Character")->str:
        dmg = target.harm(12)
        return f'The battering hail inflicts {target.name} with {dmg} damage'

class Wind(Weather):
    def __init__(self):
        super().__init__("wind", "The strong winds blow mightily...")

    def doApplyEffect(self, target: "Character")->str:
        boost = Boost("control", 0.15, 1)
        withPotencyApplied = target.boost(boost)
        return f'The driving wind inflicts {target.name} with {withPotencyApplied.get_boost_text()}'

class Clear(Weather):
    def __init__(self):
        super().__init__("no weather", "The land is seized by an undying calm...")

    def doApplyEffect(self, target: "Character")->str:
        return ""



LIGHNING_WEATHER = Lightning()
RAIN_WEATHER = Rain()
HAIL_WEATHER = Hail()
WIND_WEATHER = Wind()
NO_WEATHER = Clear()

WEATHERS = (
    LIGHNING_WEATHER,
    RAIN_WEATHER,
    HAIL_WEATHER,
    WIND_WEATHER,
    NO_WEATHER
)
