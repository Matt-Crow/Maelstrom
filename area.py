from utilities import *
from navigate import script_file
from battle import Battle
from file import File
from output import Op

class Area:
    def __init__(self, name, locations=[], levels=[]):
        self.name = name
        self.description = ignore_text(script_file.grab_key(name)[0], File.description_key)
        self.locations = to_list(locations)
        self.levels = to_list(levels)
        self.levels.append(Battle.generate_random())

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
