from utilities import contains, ignore_text
from navigate import script_file
from story import Story
from output import Op
from file import File

class Location:
    """
    Locations are used to store text descriptions of an area,
    providing a bit of atmosphere
    """
    def __init__(self, name):
        """
        Creates a location with the given name.
        If the name exists in script.txt, will add
        this' description and story automatically.
        Will change how script works later.
        """
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

            if mode == "script" and (not line.isspace()):
                script_list.append(ignore_text(line, File.script_key))

            if len(script_list) is not 0:
                self.script = Story(script_list)
    
    def get_data(self):
        """
        Get data for outputting
        """
        return [self.name, "\t" + self.description]
    
    def travel_to(self, player):
        """
        Prints this location's story,
        then calls this' action method,
        passing in the given player
        """
        self.script.print_story()
        self.action(player)

    def action(self, player):
        """
        Can be overrided to allow
        players to interact with this
        location.
        """
        return False
