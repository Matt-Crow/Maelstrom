"""
This module contains functions used to display each metaphorical page of the app.
In the future, this may be refactored to be more polymorphic,
as users will be able to view pages as either console or GUI.
"""

from maelstrom.campaign.area import Area
from maelstrom.choices import ChooseAction, ChooseOneOf, ChooseOneOrNone
from maelstrom.dataClasses.character import Character
from maelstrom.dataClasses.customizable import AbstractCustomizable
from maelstrom.dataClasses.item import getItemList
from maelstrom.dataClasses.passiveAbilities import getPassiveAbilityList
from maelstrom.dataClasses.team import Team
from maelstrom.inputOutput.screens import Screen
from maelstrom.util.stringUtil import lengthOfLongest
from maelstrom.util.user import User

class Pages:
    def main_menu(self, choose_action: ChooseAction):
        """
        Displays the main menu and asks the user to choose an option
        """

        Screen().display_and_choose("Choose an option:", choose_action)
    
    def login_menu(self, choice: ChooseOneOrNone):
        """
        Display the login menu and asks the user who to log in as
        """
        Screen("Login").display_and_choose("Which user are you?", choice)
    
    def new_user_menu(self, element_choice: ChooseOneOf[str]) -> str:
        """
        Asks the user to create an account.
        Returns the name of their account they choose.
        """
        name = input("What do you want your character's name to be? ")
        screen = Screen("New User")
        screen.add_body_row("Each character has elemental powers, what element do you want yours to control?")
        screen.display_and_choose("Choose an element:", element_choice)
        return name

    def display_user(self, user: User):
        """
        Displays information about the given user
        """
        screen = Screen(user.name)
        screen.add_body_rows(user.getDisplayData())
        screen.display()
    
    def display_and_choose_action(self, choose_action: ChooseAction):
        Screen().display_and_choose("What do you wish to do?", choose_action)

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
        screen = Screen(f'Manage {user_name}')
        screen.add_body_rows([member.getDisplayData() for member in characters])
        screen.display_and_choose("Who do you wish to manage?", choice)
    
    def display_and_choose_manage_character(self, character: Character, choose_what_to_manage: ChooseOneOrNone):
        screen = Screen(f'Manage {character.name}')
        screen.add_body_rows([str(item) for item in character.equippedItems])
        screen.display_and_choose("What do you want to customize?", choose_what_to_manage)
    
    def display_and_customize(self, customizable: AbstractCustomizable):
        """
        Allows user to customize stats
        """

        if customizable.customizationPoints <= 0:
            return
        
        screen = Screen(f'Cusomizing {customizable.name}')
        screen.add_body_rows(customizable.getStatDisplayList())
            
        choose_stat_to_increase = ChooseOneOrNone(
            options=[stat.name for stat in customizable.stats.values() if not stat.is_max()],
            none_of_these="Save chanages and exit",
            handle_choice=lambda stat_name: self._display_and_customize_part_2(customizable, screen, stat_name),
            handle_none=lambda: None
        )
        screen.display_and_choose("Which stat do you want to increase?", choose_stat_to_increase)
    
    def _display_and_customize_part_2(self, customizable: AbstractCustomizable, screen: Screen, increaseMe: str):
        # choose different stat to decrease
        choose_stat_to_decrease = ChooseOneOrNone(
            options=[stat.name for stat in customizable.stats.values() if not stat.is_min() and stat.name != increaseMe],
            none_of_these="Exit",
            handle_choice=lambda d: self._display_and_customize_part_3(customizable, increaseMe, d),
            handle_none=lambda: None
        )
        screen.display_and_choose("Which stat do you want to decrease?", choose_stat_to_decrease)

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
        screen = Screen(area.name)
        screen.add_body_row(area.getDisplayData())
        screen.display_and_choose("Choose a level to play:", choose_level)
    
    def display_encounter_start(self, playerTeam: Team, enemyTeam: Team, body_rows: list[str]):
        screen = Screen(f'{playerTeam.name} VS. {enemyTeam.name}')
        playerTeamData = getTeamDisplayData(playerTeam)
        enemyTeamData = getTeamDisplayData(enemyTeam)
        screen.add_split_row(playerTeamData, enemyTeamData)
        screen.add_body_rows(body_rows)
        screen.display()

    def display_start_of_character_turn(self, whos_turn_it_is: Character, attacking_team: Team, defending_team: Team, messages: list[str]):
        screen = self.set_up_screen_for_turn(whos_turn_it_is, attacking_team, defending_team, messages)
        screen.display()

    def display_encounter_end(self, title: str, body_rows: list[str]):
        screen = Screen(title)
        screen.add_body_rows(body_rows)
        screen.display()

    def set_up_screen_for_turn(self, whos_turn_it_is: Character, attacking_team: Team, defending_team: Team, messages: list[str]) -> Screen:
        screen = Screen(f'{whos_turn_it_is}\'s turn')
        screen.add_split_row(
            getTeamDisplayData(attacking_team),
            getTeamDisplayData(defending_team)
        )
        screen.add_body_rows(messages)
        return screen

    def _display_simple(self, rows: list[str]):
        screen = Screen()
        screen.add_body_rows(rows)
        screen.display()


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