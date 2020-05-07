from utilities import *
from battle import Battle
from output import Op
from serialize import AbstractJsonSerialable
import json
import os

AREA_DIRECTORY = 'maelstrom_story/areas'
class Area(AbstractJsonSerialable):
    """
    An Area is a collection of story elements and battles.

    required kwargs:
    - name : str
    - desc : str
    - locations : list of Locations. Defaults to []
    - levels : list of Battles. Defaults to []
    """
    def __init__(self, **kwargs):
        super(Area, self).__init__(**dict(kwargs, type="Area"))
        self.name = kwargs["name"]
        self.desc = kwargs["desc"]
        self.locations = kwargs.get("locations", [])
        self.levels = kwargs.get("levels", [])

        self.addSerializedAttributes(
            "name",
            "desc",
            "locations",
            "levels"
        )
        #self.levels.append(Battle.generate_random())

    @staticmethod
    def createDefaultArea()->"Area":
        return Area(
            name="Test Area",
            desc="No description"
        )

    @staticmethod
    def loadDefault():
        jdict = {}
        with open(os.path.join(AREA_DIRECTORY, "Ancient caverns".replace(" ", "_") + ".json"), 'rt') as file:
            jdict = json.loads(file.read())
        return Area.loadJson(jdict)

    @staticmethod
    def loadJson(jdict: dict):
        dict["locations"] = [Location.loadJson(j) for j in jdict["locations"]]
        dict["levels"] = [Battle.loadJson(j) for j in jdict["levels"]]
        return Area(**dict)

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
        options.append("Manage")
        options.append("Quit")

        choice = choose("What do you wish to do?", options)
        if choice == "Level":
            lvChoice = choose("Which level do you want to play?", self.levels)
            lvChoice.load_team(player)
            lvChoice.play()
        elif choice == "Manage":
            player.manage()
        elif choice == "Location":
            travelChoice = choose("Where do you want to go?", self.locations)
            travelChoice.travelTo()

        # will want to move this somewhere else.
        if choice != "Quit":
            self.chooseAction(player)





"""
Locations are used to store text descriptions of an area,
providing a bit of atmosphere
"""
class Location(AbstractJsonSerialable):
    def __init__(self, name: str, desc: str, script: list):
        super(Location, self).__init__(type="Location")
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
