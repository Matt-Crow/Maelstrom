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

    def display_data(self, player):
        Op.add("Area: " + self.name)
        Op.indent(4)
        Op.add(self.description)
        Op.indent(-4)
        Op.add("Locations:")
        Op.indent(4)
        for loc in self.locations:
            Op.add(loc.get_data())
        Op.indent(-4)
        Op.add("Levels:")
        Op.indent(4)
        for level in self.levels:
            Op.add(level.get_data())
        Op.indent(-4)
        Op.display()
        self.trav_or_play(player)
    def __str__(self):
        return self.name

    def trav_or_play(self, player):
        choice = choose("What do you wish to do?", ("Location", "Level", "Customize", "Quit"))
        if choice == "Level":
            level_to_play = choose("Which level do you want to play?", self.levels)
            level_to_play.load_team(player)
            level_to_play.play()

        elif choice == "Customize":
            player.customize()

        elif choice == "Location":
            place_to_go = choose("Where do you want to go?", self.locations)
            place_to_go.travel_to(player)

        if choice != "Quit":
            self.display_data(player)
