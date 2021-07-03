from util.output import Op
from teams import PlayerTeam, AbstractTeam
from character import AbstractCharacter, EnemyCharacter
from utilities import choose, ELEMENTS
from area import Area
import json
from fileSystem import getUserList

from inputOutput.screens import Screen, AreaScreen, GameScreen, SimplerGameScreen, displayCharacterStats, RowContentStyle


"""
The Game class is used to store data on the game the user is currently playing,
so this way, there don't have to be any globals.
"""
class Game:
    def __init__(self):
        self.playerTeam = None
        self.currentArea = None
        self.exit = False

    def test(self):
        """
        screen = Screen()
        screen.add(77, 0, "Yum")
        screen.add(79, 10, "Vertical")
        screen.add(40, 20, "Hello world!")
        screen.add(60, 25, "This line will be cut off")
        screen.add(70, 30, "This has a bunch of \n new \n lines")
        screen.display()
        AreaScreen(Area.createDefaultArea()).display()
        GameScreen().display()
        """
        scr = SimplerGameScreen()
        scr.addSplitRow("alpha" * 20, "beta\ngamma\n\tdelta\nsomething else entirely")
        scr.addBodyRow("ahh " * 50)
        for i in range(20):
            scr.addOption(f'f({i}) = {32 - i * i}')
        scr.addOption("Jeff")
        scr.display()

        for line in RowContentStyle(8).format("#" * 60):
            print(f'|{line}|')

        #EnemyCharacter.generateEnemies()

    def chooseAction(self):
        options = ["explore", "view character info", "customize character", "exit"]
        choice = choose("What do you wish to do?", options)
        if choice == "explore":
            self.currentArea.chooseAction(self.playerTeam)
        elif choice == "view character info":
            # This will change to display the entire team if I change back to
            # more than one member per player team
            displayCharacterStats(self.playerTeam.getMember())
        elif choice == "customize character":
            self.playerTeam.manage()
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
            if self.playerTeam == None:
                self.mainMenu()
            else:
                self.chooseAction()
        if self.playerTeam is not None:
            self.playerTeam.save()

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
        self.playerTeam = PlayerTeam.loadUser(userName)
        self.playerTeam.initForBattle()
        # This will change to display the entire team if I change back to
        # more than one member per player team
        displayCharacterStats(self.playerTeam.getMember())

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
