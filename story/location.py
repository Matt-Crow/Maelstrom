from serialize import AbstractJsonSerialable
from output import Op

"""
Locations are used to store text descriptions of an area,
providing a bit of atmosphere
"""
class Location(AbstractJsonSerialable):
    def __init__(self, name: str, desc: str, script: list):
        super(Location, self).__init__("Location")
        self.name = name
        self.desc = desc
        self.script = script
        self.addSerializedAttributes(
            "name",
            "desc",
            "script"
        )

    @staticmethod
    def loadJson(jdict: dict):
        return Location(jdict["name"], jdict["desc"], jdict["script"])

    """
    Get data for outputting
    """
    def getDisplayData(self):
        return [self.name, "\t" + self.desc]


    """
    Prints this location's story,
    then calls this' action method,
    passing in the given player
    """
    def travelTo(self):
        for line in self.script:
            Op.add(line)
            Op.display()
