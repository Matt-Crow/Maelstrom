"""
This module replaces the old distinction between player and AI teams
"""



from maelstrom.dataClasses.characterManager import manageCharacter
from maelstrom.inputOutput.teamDisplay import getDetailedTeamData
from inputOutput.screens import Screen
from util.serialize import AbstractJsonSerialable # old util package



class User(AbstractJsonSerialable):
    """
    A User simply contains a name, team, and inventory.
    Future versions will also store campaign info and other choices in this
    """

    def __init__(self, **kwargs):
        """
        required kwargs:
        - name: str
        - team: Team
        - inventory: list of Items (defaults to [])
        """
        super().__init__(**dict(kwargs, type="User"))
        self.name = kwargs["name"]
        self.team = kwargs["team"]
        self.inventory = kwargs.get("inventory", [])

        self.addSerializedAttributes("name", "team", "inventory")

    def acquire(self, item):
        self.inventory.append(item)

    def getAvailableItems(self):
        return [item for item in self.inventory if not item.equipped]

    def manage(self):
        """
        Displays the team management menu
        """

        screen = Screen()
        screen.setTitle(f'Manage {self.name}')
        options = ["Exit"]
        for member in self.team.members:
            screen.addBodyRow(member.getDisplayData())
            options.insert(0, member)

        for option in options:
            screen.addOption(option)

        managing = screen.displayAndChoose("Who do you wish to manage?")

        if managing is not "Exit":
            manageCharacter(managing)

    def getDisplayData(self)->"List<str>":
        return [
            f'User {self.name}',
            f'Team:',
            "\n".join(getDetailedTeamData(self.team)),
            f'Items: {", ".join([str(item) for item in self.inventory])}'
        ]
