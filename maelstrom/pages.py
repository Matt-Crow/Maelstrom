"""
This module contains functions used to display each metaphorical page of the app.
In the future, this may be refactored to be more polymorphic,
as users will be able to view pages as either console or GUI.
"""

from typing import Callable
from maelstrom.campaign.area import Area
from maelstrom.dataClasses.activeAbilities import TargetOption
from maelstrom.dataClasses.character import Character
from maelstrom.dataClasses.customizable import AbstractCustomizable
from maelstrom.dataClasses.elements import ELEMENTS
from maelstrom.dataClasses.item import getItemList
from maelstrom.dataClasses.passiveAbilities import getPassiveAbilityList
from maelstrom.dataClasses.team import Team
from maelstrom.inputOutput.screens import Screen
from maelstrom.util.stringUtil import lengthOfLongest
from maelstrom.util.user import User

class Pages:
    def main_menu(self, options: list[str]) -> str:
        """
        Displays the main menu and asks the user to choose an option
        """
        return Screen().display_and_choose("Choose an option:", options)
    
    def login_menu(self, users: list[User]) -> str:
        """
        Display the login menu and asks the user who to log in as
        """
        screen = Screen("Login")
        
        options = [str(user) for user in users]
        options.append("New user")
        action = screen.display_and_choose("Which user are you?", options)

        return action
    
    def new_user_menu(self) -> list[str]:
        """
        Asks the user to create an account,
        then returns [name, element].
        """
        name = input("What do you want your character's name to be? ")
        screen = Screen("New User")
        screen.add_body_row("Each character has elemental powers, what element do you want yours to control?")
        element = screen.display_and_choose("Choose an element: ", ELEMENTS)
        return [name, element]

    def display_user(self, user: User):
        """
        Displays information about the given user
        """
        screen = Screen(user.name)
        screen.add_body_rows(user.getDisplayData())
        screen.display()
    
    def display_and_choose_action(self, options: list[str]) -> str:
        """
        Displays the given list of options and asks the user to choose one,
        then returns their choice.
        """
        screen = Screen()
        choice = screen.display_and_choose("What do you wish to do?", options)
        return choice

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
    
    def display_and_choose_manage(self, user_name: str, characters: list[Character]) -> any:
        """
        Shows the user's party and asks them who they wish to manage, or exit.
        """
        screen = Screen(f'Manage {user_name}')
        screen.add_body_rows([member.getDisplayData() for member in characters])
        options = characters.copy()
        options.append("Exit")
        choice = screen.display_and_choose("Who do you wish to manage?", options)
        return choice
    
    def display_and_choose_manage_character(self, character: Character) -> str:
        options = ["Quit", character]
        screen = Screen(f'Manage {character.name}')
        if True: # needs to check it items available
            options.append("Equipped items")

        screen.add_body_rows([str(item) for item in character.equippedItems])
        options.extend(character.equippedItems)

        # todo: add option to change passives
        # todo: add option to change actives

        options.reverse()
        customize = screen.display_and_choose("What do you want to customize?", options)
        return customize
    
    def display_and_customize(self, customizable: AbstractCustomizable):
        """
        Allows user to customize stats
        """
        while customizable.customizationPoints > 0:
            exit = "Save changes and exit"
            stats = customizable.stats.values()
            screen = Screen(f'Cusomizing {customizable.name}')
            screen.add_body_rows(customizable.getStatDisplayList())
            
            # choose stat to increase
            options = [stat.name for stat in stats if not stat.is_max()] 
            options.append(exit)
            increaseMe = screen.display_and_choose("Which stat do you want to increase?", options)
            if increaseMe == exit:
                return
            
            # choose different stat to decrease
            options = [stat.name for stat in stats if not stat.is_min() and stat.name != increaseMe]
            options.append(exit)
            decreaseMe = screen.display_and_choose("Which stat do you want to decrease?", options)
            if decreaseMe == exit:
                return

            customizable.setStatBase(increaseMe, customizable.stats[increaseMe].get_base() + 1)
            customizable.setStatBase(decreaseMe, customizable.stats[decreaseMe].get_base() - 1)
            customizable.calcStats()
            customizable.customizationPoints -= 1
    
    def display_and_choose_level(self, area: Area) -> str:
        """
        Displays the levels in an area and asks the user which one to play.
        """
        screen = Screen(area.name)
        screen.add_body_row(area.getDisplayData())
        options = area.levels.copy()
        options.append("quit")
        choice = screen.display_and_choose("Choose a level to play:", options)
        return choice
    
    def display_encounter_start(self, playerTeam: Team, enemyTeam: Team, body_rows: list[str]):
        screen = Screen(f'{playerTeam.name} VS. {enemyTeam.name}')
        playerTeamData = getTeamDisplayData(playerTeam)
        enemyTeamData = getTeamDisplayData(enemyTeam)
        screen.add_split_row(playerTeamData, enemyTeamData)
        screen.add_body_rows(body_rows)
        screen.display()

    def display_and_choose_combat_action(self, character: Character, attackerTeam: Team, defenderTeam: Team, msgs: list[str], chooseAction: Callable[[Character, Screen], TargetOption]):
        screen = Screen(f'{character}\'s turn')
        screen.add_split_row(
            getTeamDisplayData(attackerTeam),
            getTeamDisplayData(defenderTeam)
        )
        screen.add_body_rows(msgs)
        choice = chooseAction(character, screen)
        screen.add_body_row(choice.use())
        screen.add_body_rows(defenderTeam.updateMembersRemaining())
        screen.display()

    def display_encounter_end(self, title: str, body_rows: list[str]):
        screen = Screen(title)
        screen.add_body_rows(body_rows)
        screen.display()

    def _display_simple(rows: list[str]):
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