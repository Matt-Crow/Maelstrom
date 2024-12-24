from maelstrom.dataClasses.createDefaults import createDefaultPlayer
from maelstrom.dataClasses.item import getItemList
from maelstrom.dataClasses.passiveAbilities import getPassiveAbilityList
from maelstrom.dataClasses.team import Team
from maelstrom.gameplay.levelController import chooseUserAreaAction
from maelstrom.inputOutput.screens import Screen
from maelstrom.loaders.campaignloader import make_default_campaign_loader
from maelstrom.loaders.characterLoader import EnemyLoader
from maelstrom.util.user import User
from maelstrom.util.userLoader import UserLoader

from maelstrom.dataClasses.elements import ELEMENTS



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
        self.enemy_loader = EnemyLoader()
        self.campaign_loader = make_default_campaign_loader()

    def test(self):
        print("nothing to test")

    def chooseAction(self):
        screen = Screen()
        options = ["explore", "view character info", "customize character", "list passives", "list items", "exit"]
        choice = screen.display_and_choose("What do you wish to do?", options)
        if choice == "explore":
            chooseUserAreaAction(self.user, self.currentArea, self.enemy_loader)
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
        elif choice == "list items":
            screen = Screen()
            for item in getItemList():
                screen.addBodyRow(str(item))
            screen.display()
        elif choice == "exit":
            self.exit = True
        else:
            raise Exception("Unsupported choice in game.py Game.chooseAction: '{0}''".format(choice))

    """
    Begins the program
    """
    def run(self):
        campaign = self.campaign_loader.get_all()[0] # todo current user's campaign
        self.currentArea = campaign.get_area(0) # todo player chooses
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
        action = screen.display_and_choose("Choose an option: ", ["Play", "About", "Quit"])
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
        action = screen.display_and_choose("Do you wish to load a game or start a new one?", options)
        if action == "Load game":
            users.append("None of these")
            userName = screen.display_and_choose("Which user are you?", users)
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
        element = screen.display_and_choose("Choose an element: ", ELEMENTS)
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
            team = Team(
                name=userName,
                members=[character]
            )
            user = User(name=userName, team=team)
            self.userLoader.save(user)

        return ret
