from utilities import *
from location import Location
from battle import Battle
from output import Op
import json

AREA_DIRECTORY = 'maelstrom_story/areas'
class Area:
    def __init__(self, name, locations=[], levels=[]):
        self.name = name
        self.locations = to_list(locations)
        self.levels = to_list(levels)
        
        with open(AREA_DIRECTORY + '/' + name.lower().replace(' ', '_') + '.json', 'rt') as file:
            jdict = json.loads(file.read())
            self.description = jdict.get('desc', 'NO DESCRIPTION')
            self.locations = [Location(data) for data in jdict.get('locations', [])]
            self.levels = [Battle.read_json(data) for data in jdict.get('levels', [])]
        
        #self.levels.append(Battle.generate_random())


    def get_data(self):
        ret = []
        ret.append("Area: " + self.name)
        ret.append("\t" + self.description)
        ret.append("Locations:")
        for loc in self.locations:
            for line in loc.get_data():
                ret.append("\t" + line)
        ret.append("Levels:")
        for level in self.levels:
            for line in level.get_data():
                ret.append("\t" + line)
        return ret
        
        
    def get_as_json(self) -> dict:
        """
        Gets this as a dictionary that
        can be converted to JSON
        """
        return {
            'name' : self.name,
            'type' : 'area',
            'desc' : self.description,
            'locations' : [loc.get_as_json() for loc in self.locations],
            'levels' : [battle.get_as_json() for battle in self.levels]
        }


    def save(self):
        """
        Saves this' JSON to a file in
        the area directory
        """
        with open(AREA_DIRECTORY + '/' + self.name.lower().replace(' ', '_') + '.json', 'wt') as file:
            file.write(json.dumps(self.get_as_json()))
        
        
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
