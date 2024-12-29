from maelstrom.choices import ActionMapping, ChooseAction, ChooseOneOf, ChooseOneOrNone
from maelstrom.dataClasses.character import Character
from maelstrom.dataClasses.createDefaults import createDefaultPlayer
from maelstrom.dataClasses.elements import ELEMENTS
from maelstrom.dataClasses.team import Team
from maelstrom.gameplay.combat import play_level
from maelstrom.loaders.campaignloader import make_default_campaign_loader
from maelstrom.loaders.characterLoader import EnemyLoader
from maelstrom.ui import Screen
from maelstrom.ui_console import ConsoleUI
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
        self._exit = False
        self.userLoader = UserLoader()
        self.enemy_loader = EnemyLoader()
        self.campaign_loader = make_default_campaign_loader()
        self._ui = ConsoleUI()

    def test(self):
        print("nothing to test")

    def run(self):
        """
        Begins the program
        """
        campaign = self.campaign_loader.get_all()[0] # todo current user's campaign
        self.currentArea = campaign.get_area(0) # todo player chooses
        while not self._exit:
            if self.user == None:
                self._login_page()
            else:
                self._choose_action()
        if self.user is not None:
            self.userLoader.save(self.user)

    def _login_page(self):
        screen = Screen("Login")
        login_choice = ChooseOneOrNone(
            options = [str(user) for user in self.userLoader.getOptions()],
            none_of_these = "New user",
            handle_choice = lambda user_name: self._handle_login(user_name),
            handle_none = lambda: self._handle_new_user()
        )
        self._ui.display_choice("Which user are you?", login_choice, screen)

    def _handle_login(self, user_name):
        self.user = self.userLoader.load(user_name)
        self.user.team.initForBattle()

    def _handle_new_user(self):
        user_name = input("What do you want your character's name to be? ") # yuck
        if user_name in self.userLoader.getOptions():
            screen = Screen(
                title="Error Creating Account",
                body_rows=[f'The username {user_name} is already taken.']
            )
            self._ui.display(screen)
            return
        
        screen = Screen(
            title="New User",
            body_rows=["Each character has elemental powers, what element do you want yours to control?"]
        )
        element_choice = ChooseOneOf(ELEMENTS, lambda e: self._handle_element_choice(user_name, e))
        self._ui.display_choice("Choose an element:", element_choice, screen)

    def _handle_element_choice(self, user_name: str, element: str):
        character = createDefaultPlayer(user_name, element)
        team = Team(
            name=user_name,
            members=[character]
        )
        user = User(name=user_name, team=team)
        self.userLoader.save(user)
        self._handle_login(user_name)

    def _choose_action(self):
        choose_action = ChooseAction([
            ActionMapping("Explore", lambda: self._explore()),
            ActionMapping("View Party Info", lambda: self._display_party()),
            ActionMapping("Customize Character", lambda: self._choose_who_to_customize()),
            ActionMapping("Exit", lambda: self._exit_action())
        ])
        self._ui.display_choice("What do you wish to do?", choose_action, Screen())

    def _explore(self):
        screen = Screen(
            title=self.currentArea.name,
            body_rows=[self.currentArea.getDisplayData()]
        )
        choose_level = ChooseOneOrNone(
            options=self.currentArea.levels,
            none_of_these="Quit",
            handle_choice=lambda level: play_level(self._ui, level, self.user, self.enemy_loader),
            handle_none=lambda: None
        )
        self._ui.display_choice("Choose a level to play:", choose_level, screen)
    
    def _display_party(self):
        screen = Screen(
            title=self.user.name,
            body_rows=self.user.getDisplayData()
        )
        self._ui.display(screen)

    def _choose_who_to_customize(self):
        screen = Screen(
            title=f'Manage {self.user.name}',
            body_rows=[member.getDisplayData() for member in self.user.team.members]
        )
        choose_who_to_customize = ChooseOneOrNone(
            options=self.user.team.members,
            none_of_these="Exit",
            handle_choice=lambda c: self._customize_character_part1(c),
            handle_none=lambda: None # do nothing on none
        )
        self._ui.display_choice("Who do you wish to manage?", choose_who_to_customize, screen)
    
    def _customize_character_part1(self, character: Character):
        if character.customizationPoints <= 0:
            return
        
        screen = Screen(
            title=f'Cusomizing {character.name}',
            body_rows=character.getStatDisplayList()
        )
            
        choose_stat_to_increase = ChooseOneOrNone(
            options=[stat.name for stat in character.stats.values() if not stat.is_max()],
            none_of_these="Save chanages and exit",
            handle_choice=lambda stat_name: self._customize_character_part2(character, stat_name),
            handle_none=lambda: None
        )
        self._ui.display_choice("Which stat do you want to increase?", choose_stat_to_increase, screen)

    def _customize_character_part2(self, character: Character, increase_me: str):
        screen = Screen(f'Cusomizing {character.name}')
        # choose different stat to decrease
        choose_stat_to_decrease = ChooseOneOrNone(
            options=[stat.name for stat in character.stats.values() if not stat.is_min() and stat.name != increase_me],
            none_of_these="Exit",
            handle_choice=lambda d: self._display_and_customize_part_3(character, increase_me, d),
            handle_none=lambda: None
        )
        self._ui.display_choice("Which stat do you want to decrease?", choose_stat_to_decrease, screen)

    def _display_and_customize_part_3(self, character: Character, increase_me: str, decrease_me: str):
        character.setStatBase(increase_me, character.stats[increase_me].get_base() + 1)
        character.setStatBase(decrease_me, character.stats[decrease_me].get_base() - 1)
        character.calcStats()
        character.customizationPoints -= 1
        
        # make recursive call
        self._customize_character_part1(character) 

    def _exit_action(self):
        self._exit = True
