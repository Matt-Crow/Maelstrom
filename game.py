from util.output import Op
from teams import PlayerTeam, AbstractTeam
from character import AbstractCharacter, EnemyCharacter
from utilities import choose, ELEMENTS
from area import Area
import json
from fileSystem import getUserList

from output.screens.screens import Screen

"""
The Game class is used to store data on the game the user is currently playing,
so this way, there don't have to be any globals.
"""
class Game:
    def __init__(self):
        self.player = None
        self.currentArea = None
        self.exit = False

    def test(self):
        Screen().display()
        #EnemyCharacter.generateEnemies()

    def chooseAction(self):
        options = ["explore", "view character info", "customize character", "exit"]
        choice = choose("What do you wish to do?", options)
        if choice == "explore":
            self.currentArea.chooseAction(self.player)
        elif choice == "view character info":
            self.player.displayData()
        elif choice == "customize character":
            self.player.manage()
        elif choice == "exit":
            self.exit = True
        else:
            raise Exception("Unsupported choice in game.py Game.chooseAction: '{0}''".format(choice))

    """
    Begins the program
    """
    def run(self):
        self.currentArea = Area.createDefaultArea()
        while not self.exit:
            if self.player == None:
                self.mainMenu()
            else:
                self.chooseAction()
        self.player.save()

    """
    Displayes the main menu
    """
    def mainMenu(self):
        Op.add("MAELSTROM")
        Op.display()
        action = choose("Choose an option: ", ["Play", "About", "Quit"])
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
        users = getUserList()
        userName = None
        options = ["Create game"]
        if len(users) > 0:
            options.append("Load game")

        action = choose("Do you wish to load a game, or start a new one?", options)
        if action == "Load game":
            users.append("None of these")
            userName = choose("Which user are you?", users)
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
        self.player = PlayerTeam.loadUser(userName)
        self.player.initForBattle()
        self.player.displayData()

    """
    Creates the menu for creating a new user
    """
    def newUserMenu(self):
        name = input("What do you want your character\'s name to be? ")
        element = choose("Each character has elemental powers, what element do you want yours to control?", ELEMENTS)
        result = self.createUser(name, element)
        print(result)
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

        if userName in getUserList():
            ret = "The name " + userName + " is already taken."
            success = False

        if success:
            character = AbstractCharacter.createDefaultPlayer(userName, element)
            team = PlayerTeam(
                name=userName,
                member=character
            )
            team.save()

        return ret
