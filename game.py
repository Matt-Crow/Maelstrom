from maelstrom.choices import ActionMapping, ChooseAction, ChooseOneOf, ChooseOneOrNone
from maelstrom.dataClasses.character import Character
from maelstrom.dataClasses.createDefaults import createDefaultPlayer
from maelstrom.dataClasses.elements import ELEMENTS
from maelstrom.dataClasses.team import Team
from maelstrom.gameplay.combat import play_level
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
        choose_action = ChooseAction([
            ActionMapping("Explore", lambda: self._explore()),
            ActionMapping("View Party Info", lambda: self._pages.display_user(self.user)),
            ActionMapping("Customize Character", lambda: self._choose_who_to_customize()),
            ActionMapping("List Passives", lambda: self._pages.display_all_passives()),
            ActionMapping("List Items", lambda: self._pages.display_all_items()),
            ActionMapping("Exit", lambda: self._exit_action())
        ])
        self._pages.display_and_choose_action(choose_action)

    def _explore(self):
        choose_level = ChooseOneOrNone(
            options=self.currentArea.levels,
            none_of_these="Quit",
            handle_choice=lambda level: play_level(self._pages.ui, level, self.user, self.enemy_loader),
            handle_none=lambda: None
        )
        self._pages.display_and_choose_level(self.currentArea, choose_level)

    def _choose_who_to_customize(self):
        choose_who_to_customize = ChooseOneOrNone(
            options=self.user.team.members,
            none_of_these="Exit",
            handle_choice=lambda c: self._customize_character(c),
            handle_none=lambda: None # do nothing on none
        )
        self._pages.display_and_choose_manage(self.user.name, self.user.team.members, choose_who_to_customize)

    def _customize_character(self, character: Character):
        customizables = character.equippedItems.copy()
        customizables.append(character)
        choose_what_to_manage = ChooseOneOrNone(
            options=customizables,
            none_of_these="Quit",
            handle_choice=lambda c: self._pages.display_and_customize(c),
            handle_none=lambda: None
        )
        self._pages.display_and_choose_manage_character(character, choose_what_to_manage)
    
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

    def mainMenu(self):
        """
        Displayes the main menu
        """
        choose_menu_item = ChooseAction([
            ActionMapping("Play", lambda: self._choose_login_action()),
            ActionMapping("About", lambda: None),
            ActionMapping("Quit", lambda: self._exit_action())
        ])
        self._pages.main_menu(choose_menu_item)

    def _choose_login_action(self):
        login_choice = ChooseOneOrNone(
            options = [str(user) for user in self.userLoader.getOptions()],
            none_of_these = "New user",
            handle_choice = lambda user_name: self.loginUser(user_name),
            handle_none = lambda: self.newUserMenu()
        )
        self._pages.login_menu(login_choice)

    def _exit_action(self):
        self.exit = True

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
        def handle_element_choice(choice):
            self._element = choice # yuck
            
        element_choice = ChooseOneOf(ELEMENTS, handle_element_choice)
        name = self._pages.new_user_menu(element_choice)
        result = self.createUser(name, self._element)
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