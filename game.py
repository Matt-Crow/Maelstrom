from maelstrom.dataClasses.createDefaults import createDefaultPlayer
from maelstrom.dataClasses.team import Team
from maelstrom.gameplay.combat import playLevel
from maelstrom.loaders.campaignloader import make_default_campaign_loader
from maelstrom.loaders.characterLoader import EnemyLoader
from maelstrom.pages import Pages
from maelstrom.util.user import User
from maelstrom.util.userLoader import UserLoader

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
        self._pages = Pages()

    def test(self):
        print("nothing to test")

    def chooseAction(self):
        options = ["explore", "view character info", "customize character", "list passives", "list items", "exit"]
        choice = self._pages.display_and_choose_action(options)
        if choice == "explore":
            level_choice = self._pages.display_and_choose_level(self.currentArea)
            if level_choice is not "quit":
                playLevel(level_choice, self.user, self.enemy_loader)
        elif choice == "view character info":
            self._pages.display_user(self.user)
        elif choice == "customize character":
            managing = self._pages.display_and_choose_manage(self.user.name, self.user.team.members)
            if managing != "Exit":
                customize = self._pages.display_and_choose_manage_character(managing)
                if customize != "Quit":
                    if customize == "Equipped items":
                        raise Exception("todo move item choosing to user instead of character")
                    else:
                        self._pages.display_and_customize(customize)
        elif choice == "list passives":
            self._pages.display_all_passives()
        elif choice == "list items":
            self._pages.display_all_items()
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
        action = self._pages.main_menu(["Play", "About", "Quit"])
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
        action = self._pages.login_menu(self.userLoader.getOptions())
        if action == "New user": # hard coded string... yuck
            self.newUserMenu() # logs in if successful
        else:
            self.loginUser(action)

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
        [name, element] = self._pages.new_user_menu()
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