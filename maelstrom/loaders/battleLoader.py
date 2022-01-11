


from maelstrom.util.serialize import AbstractJsonLoader
from maelstrom.dataClasses.campaign import Area, Level, Location



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
