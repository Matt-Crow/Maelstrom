


from util.serialize import AbstractJsonLoader
from battle.area import Area
from battle.weather import WEATHERS
from maelstrom.dataClasses.campaign import Level, Location
from maelstrom.loaders.characterLoader import loadItem



class AreaLoader(AbstractJsonLoader):
    """
    this will be replaced with a CampaignLoader later
    """

    def __init__(self):
        super().__init__("data.areas")

    def doLoad(self, asJson: dict)->"Area":
        asJson = asJson.copy()
        asJson["locations"] = [self.loadLocation(j) for j in asJson["locations"]]
        asJson["levels"] = [self.loadLevel(j) for j in asJson["levels"]]
        return Area(**asJson)

    def loadLocation(self, asJson: dict)->"Location":
        return Location(**asJson)

    def loadLevel(self, asJson: dict)->"Level":
        return Level(**asJson)

    def loadWeather(self, asJson: dict)->"Weather":
        name = asJson["name"]
        ret = None
        for weather in WEATHERS:
            if weather.name == name:
                ret = weather
                break
        if ret is None:
            raise Error("No weather found with name '{0}'".format(name))
        return ret
