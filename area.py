from utilities import *
from navigate import script_file
from battle import Battle
from file import File

class Area:
    def __init__(self, name, locations, levels):
        self.name = name
        self.description = ignore_text(script_file.grab_key(name)[0], File.description_key)
        self.locations = to_list(locations)
        self.levels = to_list(levels)
        self.levels.append(Battle.generate_random())

    def display_data(self, player):
        Op.add("Area: " + self.name)
        Op.indent()
        Op.add(self.description)
        Op.dp()
        Op.add("Locations:")
        Op.indent()
        for loc in self.locations:
            loc.display_data()
        Op.unindent()
        Op.add("Levels:")
        Op.indent()
        for level in self.levels:
            level.display_data()
        Op.unindent()
        self.trav_or_play(player)
    def __str__(self):
        return self.name

    def trav_or_play(self, player):
        choice = choose("Do you wish to travel to a location, play a level, customize your character, or quit?", ("Location", "Level", "Customize", "Quit"))
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
