from maelstrom.choices import ChooseOneOf, ChooseOneOrNone
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

    async def run(self):
        """
        Begins the program
        """
        campaign = self.campaign_loader.get_all()[0] # todo current user's campaign
        self.currentArea = campaign.get_area(0) # todo player chooses
        while not self._exit:
            if self.user == None:
                await self._login_page()
            else:
                await self._choose_action()
        if self.user is not None:
            self.userLoader.save(self.user)

    async def _login_page(self):
        screen = Screen(
            title="Login",
            choice=ChooseOneOrNone(
                prompt="Which user are you?",
                options = [str(user) for user in self.userLoader.getOptions()],
                none_of_these = "New user"
            )
        )
        choice = await self._ui.display_and_choose(screen)
        match choice:
            case "New user": 
                await self._handle_new_user()
            case _:
                self._handle_login(choice)

    async def _handle_new_user(self):
        user_name = input("What do you want your character's name to be? ") # yuck
        while user_name in self.userLoader.getOptions():
            screen = Screen(
                title="Error Creating Account",
                body_rows=[f'The username {user_name} is already taken.']
            )
            await self._ui.display_and_choose(screen) 
            user_name = input("What do you want your character's name to be? ") # yuck
        
        screen = Screen(
            title="New User",
            body_rows=["Each character has elemental powers, what element do you want yours to control?"],
            choice=ChooseOneOf("Choose an element:", ELEMENTS)
        )
        element = await self._ui.display_and_choose(screen)

        character = createDefaultPlayer(user_name, element)
        team = Team(
            name=user_name,
            members=[character]
        )
        user = User(name=user_name, team=team)
        self.userLoader.save(user)
        self._handle_login(user_name)
    
    def _handle_login(self, user_name):
        self.user = self.userLoader.load(user_name)
        self.user.team.initForBattle()

    async def _choose_action(self):
        screen = Screen(
            choice=ChooseOneOf("Choose an option", [
                "Explore",
                "View Party Info",
                "Customize Character",
                "Exit"
            ])
        )
        action = await self._ui.display_and_choose(screen)
        match action:
            case "Explore":
                await self._explore()
            case "View Party Info":
                await self._display_party()
            case "Customize Character":
                await self._customize_action()
            case "Exit":
                self._exit_action()

    async def _explore(self):
        screen = Screen(
            title=self.currentArea.name,
            body_rows=[self.currentArea.getDisplayData()],
            choice=ChooseOneOrNone(
                prompt="Choose a level to play:",
                options=self.currentArea.levels,
                none_of_these="Quit"
            )
        )
        level = await self._ui.display_and_choose(screen)
        if level != "Quit":
            await play_level(self._ui, level, self.user, self.enemy_loader)

    async def _display_party(self):
        screen = Screen(
            title=self.user.name,
            body_rows=self.user.getDisplayData()
        )
        await self._ui.display_and_choose(screen)

    async def _customize_action(self):
        screen = Screen(
            title=f'Manage {self.user.name}',
            body_rows=[member.getDisplayData() for member in self.user.team.members],
            choice=ChooseOneOrNone(
                prompt="Choose a character to customize",
                options=self.user.team.members,
                none_of_these="Exit"
            )
        )
        character = await self._ui.display_and_choose(screen)
        if character == "Exit":
            return
        
        done_customizing = False
        while not done_customizing:
            done_customizing = await self._customize_character(character)
    
    async def _customize_character(self, character: Character) -> bool:
        """
        Returns True once we're done customizing
        """
        
        if character.customizationPoints <= 0:
            return True
        
        screen = Screen(
            title=f'Cusomizing {character.name}',
            body_rows=character.getStatDisplayList(),
            choice=ChooseOneOrNone(
                prompt="Choose a stat to increase",
                options=[stat.name for stat in character.stats.values() if not stat.is_max()],
                none_of_these="Save chanages and exit"
            )
        )
        increase_me = await self._ui.display_and_choose(screen)
        if increase_me == "Save chanages and exit":
            return True
        
        # choose different stat to decrease
        screen = Screen(
            title=f'Cusomizing {character.name}',
            choice=ChooseOneOrNone(
                prompt="Choose a stat to decrease",
                options=[stat.name for stat in character.stats.values() if not stat.is_min() and stat.name != increase_me],
                none_of_these="Exit"
            )
        )
        decrease_me = await self._ui.display_and_choose(screen)
        if decrease_me == "Exit":
            return True
        
        character.setStatBase(increase_me, character.stats[increase_me].get_base() + 1)
        character.setStatBase(decrease_me, character.stats[decrease_me].get_base() - 1)
        character.calcStats()
        character.customizationPoints -= 1
        
        return character.customizationPoints > 0

    def _exit_action(self):
        self._exit = True
