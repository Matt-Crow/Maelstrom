


from util.loader import AbstractJsonLoader
from battle.battle import Battle
from battle.area import Area, Location
from battle.weather import Weather
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
        asJson["forecast"] = [Weather.deserializeJson(data) for data in asJson["forecast"]]
        asJson["rewards"] = [loadItem(data) for data in asJson["rewards"]]
        return Battle(**asJson)
