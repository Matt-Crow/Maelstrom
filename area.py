from utilities import *
from location import Location
from battle import Battle
from output import Op
from serialize import AbstractJsonSerialable
import json
import os

AREA_DIRECTORY = 'maelstrom_story/areas'
class Area(AbstractJsonSerialable):
    def __init__(self, name, desc, locations=[], levels=[]):
        super(Area, self).__init__(type="Area")
        self.name = name

        self.desc = desc
        self.locations = to_list(locations)
        self.levels = to_list(levels)

        self.addSerializedAttributes(
            "name",
            "desc",
            "locations",
            "levels"
        )
        #self.levels.append(Battle.generate_random())

    @staticmethod
    def loadDefault():
        jdict = {}
        with open(os.path.join(AREA_DIRECTORY, "Ancient caverns".replace(" ", "_") + ".json"), 'rt') as file:
            jdict = json.loads(file.read())
        return Area.loadJson(jdict)

    @staticmethod
    def loadJson(jdict: dict):
        return Area(
            jdict["name"],
            jdict["desc"],
            [Location.loadJson(j) for j in jdict["locations"]],
            [Battle.loadJson(j) for j in jdict["levels"]]
        )

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

        #                                                                 Move this to Game
        choice = choose("What do you wish to do?", ("Location", "Level", "Manage", "Quit"))
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

def generateDefaultAreas():
    pass
