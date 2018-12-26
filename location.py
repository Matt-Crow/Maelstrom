from utilities import Op, contains, ignore_text
from navigate import script_file
from story import Story
from file import File

class Location:
    def __init__(self, name):
        self.name = name

        self.all_text = script_file.grab_key(name)
        self.description = " "
        self.script = Story(" ")

        script_list = list()

        mode = None
        for line in self.all_text:
            if contains(line, File.description_key):
                self.description = ignore_text(line, File.description_key)

            if contains(line, File.script_key):
                mode = "script"

            if mode == "script":
                script_list.append(ignore_text(line, File.script_key))

            if len(script_list) is not 0:
                self.script = Story(script_list)

    def display_data(self):
        Op.add([self.name, self.description])
        Op.dp()

    def travel_to(self, player):
        self.script.print_story()
        self.action(player)

    def action(self, player):
        return False
