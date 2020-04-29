from utilities import *
from location import Location
from battle import Battle
from output import Op
from serialize import Jsonable, AbstractJsonSerialable
import json
import os

AREA_DIRECTORY = 'maelstrom_story/areas'
class Area(AbstractJsonSerialable):
    def __init__(self, name, locations=[], levels=[]):
        super(Area, self).__init__("Area")
        self.name = name
        self.addSerializedAttribute("name")

        self.desc = 'NO DESCRIPTION'
        self.locations = to_list(locations)
        self.levels = to_list(levels)

        self.addSerializedAttribute("desc")
        self.addSerializedAttribute("locations")
        self.addSerializedAttribute("levels")

        with open(os.path.join(AREA_DIRECTORY, name.replace(" ", "_") + ".json"), 'rt') as file:
            jdict = json.loads(file.read())
            self.desc = jdict.get('desc', 'NO DESCRIPTION')
            self.locations = [Location(data) for data in jdict.get('locations', [])]
            self.levels = [Battle.read_json(data) for data in jdict.get('levels', [])]

        #self.levels.append(Battle.generate_random())


    def get_data(self):
        ret = []
        ret.append("Area: " + self.name)
        ret.append("\t" + self.desc)
        ret.append("Locations:")
        for loc in self.locations:
            for line in loc.get_data():
                ret.append("\t" + line)
        ret.append("Levels:")
        for level in self.levels:
            for line in level.get_data():
                ret.append("\t" + line)
        return ret


    def __str__(self):
        return self.name


    def trav_or_play(self, player):
        Op.add(self.get_data())
        Op.display()
        choice = choose("What do you wish to do?", ("Location", "Level", "Manage", "Quit"))
        if choice == "Level":
            level_to_play = choose("Which level do you want to play?", self.levels)
            level_to_play.load_team(player)
            level_to_play.play()
        elif choice == "Manage":
            player.manage()
        elif choice == "Location":
            place_to_go = choose("Where do you want to go?", self.locations)
            place_to_go.travel_to(player)

        if choice != "Quit":
            self.trav_or_play(player)
