from util.serialize import AbstractJsonSerialable
from maelstrom.inputOutput.screens import Screen
from util.stringUtil import entab

class Area(AbstractJsonSerialable):
    """
    An Area is a collection of story elements and battles.

    required kwargs:
    - name : str
    - desc : str
    - locations : list of Locations. Defaults to no locations
    - levels : list of Battles. Defaults to no battles
    """
    def __init__(self, **kwargs):
        super(Area, self).__init__(**dict(kwargs, type="Area"))
        self.name = kwargs["name"]
        self.desc = kwargs["desc"]
        self.locations = kwargs.get("locations", [])
        self.levels = kwargs.get("levels", [])

        self.addSerializedAttributes(
            "name",
            "desc",
            "locations",
            "levels"
        )

    def getDisplayData(self)->str:
        ret = [
            f'Area: {self.name}',
            entab(self.desc)
        ]

        ret.append("Locations:")
        for loc in self.locations:
            ret.append(entab(loc.getDisplayData()))

        ret.append("Levels:")
        for level in self.levels:
            ret.append(entab(level.getDisplayData()))

        return "\n".join(ret)

    def chooseAction(self, user: "User"):
        options = []
        if len(self.locations) > 0:
            options.append("Location")
        if len(self.levels) > 0:
            options.append("Level")
        options.append("Quit")

        screen = Screen()
        screen.setTitle(self.name)
        screen.addBodyRow(self.getDisplayData())

        for option in options:
            screen.addOption(option)

        choice = screen.displayAndChoose("What do you wish to do?")
        if choice == "Level":
            screen.clearOptions()
            for level in self.levels:
                screen.addOption(level)
            lvChoice = screen.displayAndChoose("Which level do you want to play?")
            lvChoice.play(user)
        elif choice == "Location":
            screen.clearOptions()
            for loc in self.locations:
                screen.addOption(loc)
            travelChoice = screen.displayAndChoose("Where do you want to go?")
            travelChoice.travelTo()

"""
Locations are used to store text descriptions of an area,
providing a bit of atmosphere
"""
class Location(AbstractJsonSerialable):
    """
    required kwargs:
    - name : str
    - desc : str
    - script : list of strings. Defaults to []
    """
    def __init__(self, **kwargs):#name: str, desc: str, script: list):
        super(Location, self).__init__(**dict(kwargs, type="Location"))
        self.name = kwargs["name"]
        self.desc = kwargs["desc"]
        self.script = kwargs.get("script", [])
        self.addSerializedAttributes(
            "name",
            "desc",
            "script"
        )

    """
    Get data for outputting
    """
    def getDisplayData(self)->str:
        return f'{self.name}: {self.desc}'

    """
    Prints this location's story
    """
    def travelTo(self):
        screen = Screen()
        screen.setTitle(self.name)
        screen.addBodyRows(self.script)
        screen.display()
