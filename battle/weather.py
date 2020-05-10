import random
from stat_classes import Boost
from serialize import AbstractJsonSerialable

"""
This is what makes Maelstrom unique!
Weather provides in-battle effects
that alter the stats of characters
"""
class Weather(AbstractJsonSerialable):
    """
    Required kwargs:
    - name : str
    - msg : str
    - consumer : function accepting an AbstractCharacter as an argument
    """
    def __init__(self, **kwargs):
        super(Weather, self).__init__(**dict(kwargs, type="Weather"))
        self.name = kwargs["name"]
        self.msg = kwargs["msg"]
        self.consumer = kwargs["consumer"]
        self.addSerializedAttribute("name")

    """
    Apply stat changes
    to a list of AbstractCharacters
    """
    def applyEffect(self, affected):
        for person in affected:
            self.consumer(person)

    """
    returns a message showing
    the weather condition
    """
    def getMsg(self):
        return self.msg

LIGHNING_WEATHER = Weather(
    name="lightning",
    msg="The sky rains down its fire upon the field...",
    consumer=(lambda person : person.gainEnergy(3))
)
RAIN_WEATHER = Weather(
    name="rain",
    msg="A deluge of water pours forth from the sky...",
    consumer=(lambda person : person.heal(9))
)
HAIL_WEATHER = Weather(
    name="hail",
    msg="A light snow was falling...",
    consumer=(lambda person : person.harm(12))
)
WIND_WEATHER = Weather(
    name="wind",
    msg="The strong winds blow mightily...",
    consumer=(lambda person : person.boost(Boost("control", 15, 1, "Weather")))
)
NO_WEATHER = Weather(
    name="no weather",
    msg="The land is seized by an undying calm...",
    consumer=(lambda person : None)
)

WEATHERS = (
    LIGHNING_WEATHER,
    RAIN_WEATHER,
    HAIL_WEATHER,
    WIND_WEATHER,
    NO_WEATHER
)

def deserializeWeather(jdict: dict)->"Weather":
    name = jdict["name"]
    ret = None
    for weather in WEATHERS:
        if weather.name == name:
            ret = weather
            break
    if ret is None:
        raise Error("No weather found with name '{0}'".format(name))
    return ret
