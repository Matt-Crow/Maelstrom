from serialize import AbstractJsonSerialable
from fileSystem import AREA_DIR, loadSerializable, saveSerializable
from utilities import *
from battle import Battle
from util.output import Op

class Area(AbstractJsonSerialable):
    """
    An Area is a collection of story elements and battles.

    required kwargs:
    - name : str
    - desc : str
    - locations : list of Locations. Defaults to [Location.createDefaultLocation]
    - levels : list of Battles. Defaults to [Battle.generateRandom]
    """
    def __init__(self, **kwargs):
        super(Area, self).__init__(**dict(kwargs, type="Area"))
        self.name = kwargs["name"]
        self.desc = kwargs["desc"]
        self.locations = kwargs.get("locations", [Location.createDefaultLocation()])
        self.levels = kwargs.get("levels", [Battle.generateRandom()])

        self.addSerializedAttributes(
            "name",
            "desc",
            "locations",
            "levels"
        )

    @staticmethod
    def createDefaultArea()->"Area":
        return Area(
            name="Test Area",
            desc="No description"
        )

    @classmethod
    def deserializeJson(cls, jdict: dict)->"Area":
        jdict["locations"] = [Location.deserializeJson(j) for j in jdict["locations"]]
        jdict["levels"] = [Battle.deserializeJson(j) for j in jdict["levels"]]
        return Area(**jdict)

    @classmethod
    def loadArea(cls, areaName: str)->"Area":
        return loadSerializable(areaName, AREA_DIR, Area)

    def save(self):
        saveSerializable(self, AREA_DIR)

    def getDisplayData(self):
        ret = []
        ret.append("Area: " + self.name)
        ret.append("\t" + self.desc)
        ret.append("Locations:")
        for loc in self.locations:
            for line in loc.getDisplayData():
                ret.append("\t" + line)
        ret.append("Levels:")
        for level in self.levels:
            for line in level.getDisplayData():
                ret.append("\t" + line)
        return ret
    def displayData(self):
        Op.add(self.getDisplayData())
        Op.display()

    def __str__(self):
        return self.name


    def chooseAction(self, player):
        Op.add(self.getDisplayData())
        Op.display()

        options = []
        if len(self.locations) > 0:
            options.append("Location")
        if len(self.levels) > 0:
            options.append("Level")
        options.append("Quit")

        choice = choose("What do you wish to do?", options)
        if choice == "Level":
            lvChoice = choose("Which level do you want to play?", self.levels)
            lvChoice.play(player)
        elif choice == "Location":
            travelChoice = choose("Where do you want to go?", self.locations)
            travelChoice.travelTo()

"""
Locations are used to store text descriptions of an area,
providing a bit of atmosphere
"""
class Location(AbstractJsonSerialable):
    """
    required kwargs:
    - name : str
    - desc : str
    - script : list of strings. Defaults to []
    """
    def __init__(self, **kwargs):#name: str, desc: str, script: list):
        super(Location, self).__init__(**dict(kwargs, type="Location"))
        self.name = kwargs["name"]
        self.desc = kwargs["desc"]
        self.script = kwargs.get("script", [])
        self.addSerializedAttributes(
            "name",
            "desc",
            "script"
        )

    @staticmethod
    def createDefaultLocation():
        return Location(
            name="Shoreline",
            desc="Gentle waves lap at the shore.",
            script=[
                "I'm not sure how I feel about the sand...",
                "is it course and rough?",
                "or soft?"
            ]
        )

    @classmethod
    def deserializeJson(cls, jdict: dict)->"Location":
        return Location(**jdict)

    """
    Get data for outputting
    """
    def getDisplayData(self):
        return [self.name, "\t" + self.desc]


    """
    Prints this location's story
    """
    def travelTo(self):
        for line in self.script:
            Op.add(line)
            Op.display()
