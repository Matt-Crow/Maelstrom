"""
This module contains functions used to display each metaphorical page of the app.
In the future, this may be refactored to be more polymorphic,
as users will be able to view pages as either console or GUI.

TODO: inline methods 
"""

from maelstrom.campaign.area import Area
from maelstrom.choices import ChooseAction, ChooseOneOf, ChooseOneOrNone
from maelstrom.dataClasses.character import Character
from maelstrom.dataClasses.customizable import AbstractCustomizable
from maelstrom.dataClasses.item import getItemList
from maelstrom.dataClasses.passiveAbilities import getPassiveAbilityList
from maelstrom.dataClasses.team import Team
from maelstrom.screens import Screen
from maelstrom.util.stringUtil import lengthOfLongest
from maelstrom.util.user import User

class Pages:

    def __init__(self):
        self._ui = Screen()

    def main_menu(self, choose_action: ChooseAction):
        """
        Displays the main menu and asks the user to choose an option
        """
        self._ui.clear()
        self._ui.title = "Main Menu"
        self._ui.display_choice("Choose an option:", choose_action)
    
    def login_menu(self, choice: ChooseOneOrNone):
        """
        Display the login menu and asks the user who to log in as
        """
        self._ui.clear()
        self._ui.title = "Login"
        self._ui.display_choice("Which user are you?", choice)
    
    def new_user_menu(self, element_choice: ChooseOneOf[str]) -> str:
        """
        Asks the user to create an account.
        Returns the name of their account they choose.
        """
        name = input("What do you want your character's name to be? ") # yuck
        self._ui.clear()
        self._ui.title = "New User"
        self._ui.add_body_row("Each character has elemental powers, what element do you want yours to control?")
        self._ui.display_choice("Choose an element:", element_choice)
        return name

    def display_user(self, user: User):
        """
        Displays information about the given user
        """
        self._ui.clear()
        self._ui.title = user.name
        self._ui.add_body_rows(user.getDisplayData())
        self._ui.display()
    
    def display_and_choose_action(self, choose_action: ChooseAction):
        self._ui.clear()
        self._ui.display_choice("What do you wish to do?", choose_action)

    def display_all_passives(self):
        """
        Displays all passives available in the game
        """
        self._display_simple([passive.description for passive in getPassiveAbilityList()])

    def display_all_items(self):
        """
        Displays all items available in the game
        """
        self._display_simple([str(item) for item in getItemList()])
    
    def display_and_choose_manage(self, user_name: str, characters: list[Character], choice: ChooseOneOrNone):
        """
        Shows the user's party and asks them who they wish to manage, or exit.
        """
        self._ui.clear()
        self._ui.title = f'Manage {user_name}'
        self._ui.add_body_rows([member.getDisplayData() for member in characters])
        self._ui.display_choice("Who do you wish to manage?", choice)
    
    def display_and_choose_manage_character(self, character: Character, choose_what_to_manage: ChooseOneOrNone):
        self._ui.clear()
        self._ui.title = f'Manage {character.name}'
        self._ui.add_body_rows([str(item) for item in character.equippedItems])
        self._ui.display_choice("What do you want to customize?", choose_what_to_manage)
    
    def display_and_customize(self, customizable: AbstractCustomizable):
        """
        Allows user to customize stats
        """

        if customizable.customizationPoints <= 0:
            return
        
        self._ui.clear()
        self._ui.title = f'Cusomizing {customizable.name}'
        self._ui.add_body_rows(customizable.getStatDisplayList())
            
        choose_stat_to_increase = ChooseOneOrNone(
            options=[stat.name for stat in customizable.stats.values() if not stat.is_max()],
            none_of_these="Save chanages and exit",
            handle_choice=lambda stat_name: self._display_and_customize_part_2(customizable, self._ui, stat_name),
            handle_none=lambda: None
        )
        self._ui.display_choice("Which stat do you want to increase?", choose_stat_to_increase)
    
    def _display_and_customize_part_2(self, customizable: AbstractCustomizable, screen: Screen, increaseMe: str):
        # choose different stat to decrease
        choose_stat_to_decrease = ChooseOneOrNone(
            options=[stat.name for stat in customizable.stats.values() if not stat.is_min() and stat.name != increaseMe],
            none_of_these="Exit",
            handle_choice=lambda d: self._display_and_customize_part_3(customizable, increaseMe, d),
            handle_none=lambda: None
        )
        screen.display_choice("Which stat do you want to decrease?", choose_stat_to_decrease)

    def _display_and_customize_part_3(self, customizable: AbstractCustomizable, increaseMe: str, decreaseMe: str):
        customizable.setStatBase(increaseMe, customizable.stats[increaseMe].get_base() + 1)
        customizable.setStatBase(decreaseMe, customizable.stats[decreaseMe].get_base() - 1)
        customizable.calcStats()
        customizable.customizationPoints -= 1
        self.display_and_customize(customizable) # make recursive call

    def display_and_choose_level(self, area: Area, choose_level: ChooseOneOrNone):
        """
        Displays the levels in an area and asks the user which one to play.
        """
        self._ui.clear()
        self._ui.title = area.name
        self._ui.add_body_row(area.getDisplayData())
        self._ui.display_choice("Choose a level to play:", choose_level)
    
    def display_encounter_start(self, playerTeam: Team, enemyTeam: Team, body_rows: list[str]):
        self._ui.clear()
        self._ui.title = f'{playerTeam.name} VS. {enemyTeam.name}'
        playerTeamData = getTeamDisplayData(playerTeam)
        enemyTeamData = getTeamDisplayData(enemyTeam)
        self._ui.add_scoreboard_row(playerTeamData, enemyTeamData)
        self._ui.add_body_rows(body_rows)
        self._ui.display()

    def display_start_of_character_turn(self, whos_turn_it_is: Character, attacking_team: Team, defending_team: Team, messages: list[str]):
        screen = self.set_up_screen_for_turn(whos_turn_it_is, attacking_team, defending_team, messages)
        screen.display()

    def display_encounter_end(self, title: str, body_rows: list[str]):
        self._ui.clear()
        self._ui.title = title
        self._ui.add_body_rows(body_rows)
        self._ui.display()

    def set_up_screen_for_turn(self, whos_turn_it_is: Character, attacking_team: Team, defending_team: Team, messages: list[str]) -> Screen:
        self._ui.clear()
        self._ui.title = f'{whos_turn_it_is}\'s turn'
        self._ui.add_scoreboard_row(
            getTeamDisplayData(attacking_team),
            getTeamDisplayData(defending_team)
        )
        self._ui.add_body_rows(messages)
        return self._ui

    def _display_simple(self, rows: list[str]):
        self._ui.clear()
        self._ui.add_body_rows(rows)
        self._ui.display()


def getTeamDisplayData(team: Team)->str:
    """
    Used in the in-battle HUD
    """
    lines = [
        f'{team.name}'
    ]
    longestName = lengthOfLongest((member.name for member in team.membersRemaining))
    longestHpEnergy = lengthOfLongest((f'{str(member.remHp)} HP / {str(member.energy)} energy' for member in team.membersRemaining))
    for member in team.membersRemaining:
        uiPart = f'{str(member.remHp)} HP / {str(member.energy)} EN'
        lines.append(f'* {member.name.ljust(longestName)}: {uiPart.rjust(longestHpEnergy)}')

    return "\n".join(lines)