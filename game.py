from maelstrom.characters.specification import CharacterSpecification
from maelstrom.dataClasses.activeAbilities import createDefaultActives
from maelstrom.dataClasses.character import Character
from maelstrom.dataClasses.team import Team, User
from maelstrom.gameplay.combat import play_level
from maelstrom.loaders.campaignloader import make_default_campaign_loader
from maelstrom.loaders.character_loader import EnemyLoader
from maelstrom.loaders.character_template_loader import make_starter_template_loader
from maelstrom.loaders.user_repository import UserRepository
from maelstrom.ui import Choice, Screen
from maelstrom.ui_console import ConsoleUI
from maelstrom.util.collections import list_extend

"""
The Game class is used to store data on the game the user is currently playing,
so this way, there don't have to be any globals.
"""
class Game:
    def __init__(self):
        self.user = None
        self.currentArea = None
        self._exit = False
        self._users = UserRepository()
        self._starters = make_starter_template_loader()
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
            self._users.save_user(self.user)

    async def _login_page(self):
        screen = Screen(
            title="Login",
            choice=Choice(
                prompt="Which user are you?",
                options = list_extend(
                    [str(user) for user in self._users.get_user_names()],
                    "New user"
                )
            )
        )
        choice = await self._ui.display_and_choose(screen)
        match choice:
            case "New user": 
                await self._handle_new_user()
            case _:
                self._handle_login(choice)

    async def _handle_new_user(self):
        user_name = input("What is your name? ") # yuck, input()
        while user_name in self._users.get_user_names():
            screen = Screen(
                title="Error Creating Account",
                body_rows=[f'The username {user_name} is already taken.']
            )
            await self._ui.display_and_choose(screen) 
            user_name = input("What is your name? ") # yuck, input()
        
        screen = Screen(
            title="New User",
            body_rows=["Four rookie warriors stand before you, ready to aid you."],
            choice=Choice(
                "Who will be your first party member?", 
                [starter.name for starter in self._starters.get_all_character_templates()]
            )
        )
        starter_name = await self._ui.display_and_choose(screen)
        starter_template = self._starters.get_character_template_by_name(starter_name)
        if starter_template is None:
            raise KeyError(f'Invalid character name: "{starter_name}"')
        starter = Character(
            template=starter_template,
            specification=CharacterSpecification(name=starter_name),
            actives=createDefaultActives(starter_template.element)
        )

        team = Team(user_name, [starter])
        user = User(user_name, team)
        self._users.save_user(user)
        self._handle_login(user_name)
    
    def _handle_login(self, user_name):
        self.user = self._users.load_user(user_name)
        self.user.team.init_for_battle()

    async def _choose_action(self):
        screen = Screen(
            choice=Choice("Choose an option", [
                "Explore",
                "View Party Info",
                "Exit"
            ])
        )
        action = await self._ui.display_and_choose(screen)
        match action:
            case "Explore":
                await self._explore()
            case "View Party Info":
                await self._display_party()
            case "Exit":
                self._exit_action()

    async def _explore(self):
        if self.currentArea is None or self.user is None:
            return
        
        screen = Screen(
            title=self.currentArea.name,
            body_rows=[self.currentArea.getDisplayData()],
            choice=Choice(
                prompt="Choose a level to play:",
                options=list_extend(self.currentArea.levels, "Quit")
            )
        )
        level = await self._ui.display_and_choose(screen)
        if level != "Quit":
            await play_level(self._ui, level, self.user, self.enemy_loader)

    async def _display_party(self):
        if self.user is None:
            return
        
        screen = Screen(
            title=self.user.name,
            body_rows=self.user.get_display_data()
        )
        await self._ui.display_and_choose(screen)

    def _exit_action(self):
        self._exit = True
