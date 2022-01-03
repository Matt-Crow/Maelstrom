from maelstrom.dataClasses.passiveAbilities import getPassiveAbilityList

from battle.teams import PlayerTeam, AbstractTeam
from util.utilities import ELEMENTS
from inputOutput.screens import Screen
from characters.characterLoader import PlayerTeamLoader, EnemyLoader
from characters.createDefaults import createDefaultArea, createDefaultPlayer



from characters.createDefaults import saveDefaultData
from maelstrom.gameplay.combat import testTargettingSystem



"""
The Game class is used to store data on the game the user is currently playing,
so this way, there don't have to be any globals.
"""
class Game:
    def __init__(self):
        self.playerTeam = None
        self.currentArea = None
        self.exit = False
        self.userLoader = PlayerTeamLoader()

    def test(self):
        #saveDefaultData()
        testTargettingSystem()

    def chooseAction(self):
        screen = Screen()
        options = ["explore", "view character info", "customize character", "list passives", "exit"]
        for option in options:
            screen.addOption(option)

        choice = screen.displayAndChoose("What do you wish to do?")
        if choice == "explore":
            self.currentArea.chooseAction(self.playerTeam)
        elif choice == "view character info":
            # This will change to display the entire team if I change back to
            # more than one member per player team
            self.playerTeam.getMember().displayStats()
        elif choice == "customize character":
            self.playerTeam.manage()
        elif choice == "list passives":
            screen = Screen()
            for passive in getPassiveAbilityList():
                screen.addBodyRow(passive.description)
            screen.display()
        elif choice == "exit":
            self.exit = True
        else:
            raise Exception("Unsupported choice in game.py Game.chooseAction: '{0}''".format(choice))

    """
    Begins the program
    """
    def run(self):
        self.currentArea = createDefaultArea()
        while not self.exit:
            if self.playerTeam == None:
                self.mainMenu()
            else:
                self.chooseAction()
        if self.playerTeam is not None:
            self.userLoader.save(self.playerTeam)

    """
    Displayes the main menu
    """
    def mainMenu(self):
        screen = Screen()
        screen.setTitle("MAELSTROM")
        for option in ["Play", "About", "Quit"]:
            screen.addOption(option)
        action = screen.displayAndChoose("Choose an option: ")
        if action == "Play":
            self.loginMenu()
        elif action == "About":
            pass
        else:
            self.exit = True

    """
    Asks the user to log in
    """
    def loginMenu(self):
        screen = Screen()
        screen.setTitle("Login")
        users = self.userLoader.getOptions()
        userName = None
        options = ["Create game"]
        if len(users) > 0:
            options.append("Load game")
        options.reverse()
        for option in options:
            screen.addOption(option)
        action = screen.displayAndChoose("Do you wish to load a game or start a new one?")
        if action == "Load game":
            screen.clearOptions()
            users.append("None of these")
            for user in users:
                screen.addOption(user)
            userName = screen.displayAndChoose("Which user are you?")
            if userName == "None of these":
                self.newUserMenu()
                self.loginMenu()
            else:
                self.loginUser(userName)
        else:
            self.newUserMenu() #logs in if successful


    """
    Play a game as the given user
    """
    def loginUser(self, userName):
        self.playerTeam = self.userLoader.load(userName)
        self.playerTeam.initForBattle()

    """
    Creates the menu for creating a new user
    """
    def newUserMenu(self):
        name = input("What do you want your character\'s name to be? ")
        screen = Screen()
        screen.setTitle("New User")
        screen.addBodyRow("Each character has elemental powers, what element do you want yours to control?")
        for element in ELEMENTS:
            screen.addOption(element)
        element = screen.displayAndChoose("Choose an element: ")
        result = self.createUser(name, element)
        if result == 'User added successfully!':
            self.loginUser(name)
        else:
            self.newUserMenu()

    """
    Adds a user.
    Returns a message based on if the profile creation was successful
    """
    def createUser(self, userName: str, element: str) -> str:
        ret = "User added successfully!"
        success = True

        if userName in self.userLoader.getOptions():
            ret = "The name " + userName + " is already taken."
            success = False

        if success:
            character = createDefaultPlayer(userName, element)
            team = PlayerTeam(
                name=userName,
                member=character
            )
            self.userLoader.save(team)

        return ret
