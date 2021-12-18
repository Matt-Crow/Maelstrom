


from util.serialize import AbstractJsonLoader
from battle.battle import Battle
from battle.area import Area, Location
from battle.weather import WEATHERS
from characters.characterLoader import loadItem



class AreaLoader(AbstractJsonLoader):
    def __init__(self):
        super().__init__("data.areas")

    def doLoad(self, asJson: dict)->"Area":
        asJson = asJson.copy()
        asJson["locations"] = [self.loadLocation(j) for j in asJson["locations"]]
        asJson["levels"] = [self.loadBattle(j) for j in asJson["levels"]]
        return Area(**asJson)

    def loadLocation(self, asJson: dict)->"Location":
        return Location(**asJson)

    def loadBattle(self, asJson: dict)->"Battle":
        asJson = asJson.copy()
        asJson["forecast"] = [self.loadWeather(data) for data in asJson["forecast"]]
        asJson["rewards"] = [loadItem(data) for data in asJson["rewards"]]
        return Battle(**asJson)

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
