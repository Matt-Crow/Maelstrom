from maelstrom.dataClasses.passiveAbilities import getPassiveAbilityList
from maelstrom.util.user import User
from maelstrom.util.userLoader import UserLoader

from battle.teams import AbstractTeam
from util.utilities import ELEMENTS
from inputOutput.screens import Screen
from characters.createDefaults import createDefaultArea, createDefaultPlayer

from characters.createDefaults import saveDefaultData



"""
The Game class is used to store data on the game the user is currently playing,
so this way, there don't have to be any globals.
"""
class Game:
    def __init__(self):
        self.user = None
        self.currentArea = None
        self.exit = False
        self.userLoader = UserLoader()

    def test(self):
        saveDefaultData()

    def chooseAction(self):
        screen = Screen()
        options = ["explore", "view character info", "customize character", "list passives", "exit"]
        for option in options:
            screen.addOption(option)

        choice = screen.displayAndChoose("What do you wish to do?")
        if choice == "explore":
            self.currentArea.chooseAction(self.user)
        elif choice == "view character info":
            screen = Screen()
            screen.setTitle(self.user.name)
            screen.addBodyRows(self.user.getDisplayData())
            screen.display()
        elif choice == "customize character":
            self.user.manage()
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
            if self.user == None:
                self.mainMenu()
            else:
                self.chooseAction()
        if self.user is not None:
            self.userLoader.save(self.user)

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
        self.user = self.userLoader.load(userName)
        self.user.team.initForBattle()

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
            team = AbstractTeam(
                name=userName,
                members=[character]
            )
            user = User(name=userName, team=team)
            self.userLoader.save(user)

        return ret
