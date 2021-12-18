import random
from stat_classes import Boost
from util.serialize import AbstractJsonSerialable

"""
This is what gives Maelstrom its name. Weather provides in-battle effects that
alter the stats of characters. This is an abstract class
"""
class Weather(AbstractJsonSerialable):

    def __init__(self, name: str, msg: str):
        super(Weather, self).__init__(**dict(name=name, type="Weather"))
        self.name = name
        self.msg = msg
        self.addSerializedAttribute("name")

    """
    returns a message showing
    the weather condition
    """
    def getMsg(self):
        return self.msg

    """
    Apply stat changes to a list of AbstractCharacters. Returns a string message
    that will be output
    """
    def applyEffect(self, affected: "List<AbstractCharacter>")->str:
        msgs = []
        for person in affected:
            msgs.append(self.doApplyEffect(person))
        return "\n".join(msgs)

    def doApplyEffect(self, target: "AbstractCharacter")->str:
        pass

class Lightning(Weather):
    def __init__(self):
        super().__init__("lightning", "The sky rains down its fire upon the field...")

    def doApplyEffect(self, target: "AbstractCharacter")->str:
        amount = target.gainEnergy(3)
        return f'The charged atmosphere provides {target.name} with {amount} energy'

class Rain(Weather):
    def __init__(self):
        super().__init__("rain", "A deluge of water pours forth from the sky...")

    def doApplyEffect(self, target: "AbstractCharacter")->str:
        amount = target.heal(9)
        return f'The restorative rain heals {target.name} by {amount} HP'

class Hail(Weather):
    def __init__(self):
        super().__init__("hail", "A light snow was falling...")

    def doApplyEffect(self, target: "AbstractCharacter")->str:
        dmg = target.harm(12)
        return f'The battering hail inflicts {target.name} with {dmg} damage'

class Wind(Weather):
    def __init__(self):
        super().__init__("wind", "The strong winds blow mightily...")

    def doApplyEffect(self, target: "AbstractCharacter")->str:
        boost = Boost("control", 15, 1, "Weather")
        withPotencyApplied = target.boost(boost)
        return f'The driving wind inflicts {target.name} with {withPotencyApplied.getDisplayData()}'

class Clear(Weather):
    def __init__(self):
        super().__init__("no weather", "The land is seized by an undying calm...")

    def doApplyEffect(self, target: "AbstractCharacter")->str:
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
