from output import Op


class Location:
    """
    Locations are used to store text descriptions of an area,
    providing a bit of atmosphere
    """
    def __init__(self, json: dict):
        """
        Reads a dictionary, taking specific attributes from it
        """
        self.name = json.get('name', 'NO NAME SET')
        self.description = json.get('desc', 'NO DESCRIPTION')
        self.script = json.get('script', ['NO SCRIPT'])


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