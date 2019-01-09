from utilities import contains, ignore_text
from navigate import script_file
from output import Op
from file import File
import json
import os

LOCATION_DIRECTORY = 'maelstrom_story/locations'

class Location:
    """
    Locations are used to store text descriptions of an area,
    providing a bit of atmosphere
    """
    def __init__(self, name):
        """
        Creates a location with the given name.
        If the name exists in the location directory,
        reads that json file, then loads this with that data
        """
        self.name = name
        
        j = {}
        try:
            with open(LOCATION_DIRECTORY + os.sep + self.name.replace(' ', '_').lower() + '.json', 'rt') as file:
                j = json.loads(file.read())
        except FileNotFoundError:
            Op.add(name + ' doesn\'t have an associated file in ' + LOCATION_DIRECTORY)
            Op.display()
        
        self.description = j.get('desc', 'NO DESCRIPTION')
        self.script = j.get('script', [])


    def get_as_json(self) -> dict:
        """
        Returns this as a dictionary,
        so it can be saved to a json file
        """
        return {
            'name' : self.name,
            'type' : 'location',
            'desc' : self.description,
            'script' : self.script
        }
        
    
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
        for line in self.script:
            Op.add(line)
            Op.display()
        self.action(player)


    def action(self, player):
        """
        Can be overrided to allow
        players to interact with this
        location.
        """
        return False
        
        
    def save(self):
        """
        Saves this location's data to a json file in the given directory
        """
        with open(LOCATION_DIRECTORY + os.sep + self.name.replace(' ', '_').lower() + '.json', 'wt') as file:
            file.write(json.dumps(self.get_as_json()))
