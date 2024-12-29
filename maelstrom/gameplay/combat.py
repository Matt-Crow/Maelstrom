"""
This module handles combat gameplay. This separates the data classes from the
functions that act on their data, preventing classes from become cumbersome
"""

from functools import reduce
from typing import Callable
from maelstrom.campaign.level import Level
from maelstrom.choices import ChooseOneOf
from maelstrom.dataClasses import character
from maelstrom.dataClasses.activeAbilities import TargetOption
from maelstrom.dataClasses.team import Team
from maelstrom.dataClasses.weather import WEATHERS, Weather
from maelstrom.loaders.characterLoader import EnemyLoader
from maelstrom.pages import Pages, getTeamDisplayData
from maelstrom.ui import AbstractUserInterface, Screen
from maelstrom.util.user import User

import random

def playLevel(level: Level, user: User, enemyLoader: EnemyLoader):
    """
    used to start and run a Level
    """

    enemies = [enemyLoader.load(enemyName) for enemyName in level.enemy_names]
    for enemy in enemies:
        enemy.level = level.enemy_level
    enemyTeam = Team(name="Enemy Team", members=enemies)
    enemyTeam.initForBattle()

    playerTeam = user.team
    playerTeam.initForBattle()

    weather = random.choice(WEATHERS)
    
    Pages().display_encounter_start(playerTeam, enemyTeam, [level.prescript, weather.getMsg()])

    Encounter(playerTeam, enemyTeam, weather, lambda winner: handle_team_win(level, playerTeam, enemyTeam, winner)).run()

def handle_team_win(level: Level, player_team: Team, enemy_team: Team, winner: Team):
    msgs = []
    if player_team is winner:
        msgs.append(f'{player_team.name} won!')
        msgs.append(level.postscript)
    else:
        msgs.append("Regretably, you have not won this day. Though someday, you will grow strong enough to overcome this challenge...")
    xp = enemy_team.getXpGiven()
    for member in player_team.members:
        msgs.extend(member.gainXp(xp))

    Pages().display_encounter_end(f'{player_team.name} VS. {enemy_team.name}', msgs)

class Encounter:
    """
    An encounter handles team versus team conflict.
    """

    def __init__(self, team1: Team, team2: Team, weather: Weather, handle_team_win: Callable[[Team], None]):
        self.team1 = team1
        self.team2 = team2
        self.weather = weather
        self._pages = Pages()
        self._handle_team_win = handle_team_win

    def run(self):
        """
        Runs the encounter until one team wins
        """
        self.team1.enemyTeam = self.team2
        self.team2.enemyTeam = self.team1
        self.team1.initForBattle()
        self.team2.initForBattle()
        
        while not self._is_over():
            self._player_team_turn() # recursively calls enemy team turn

        self.team1.enemyTeam = None
        self.team2.enemyTeam = None

    def _is_over(self) -> bool:
        return self.team1.isDefeated() or self.team2.isDefeated()

    def _player_team_turn(self):
        self._team_turn(self.team1, self.team2, self._user_choose)

        if self.team2.isDefeated():
            self._handle_team_win(self.team1)
            return
        
        self._ai_team_turn()
        if self.team1.isDefeated():
            self._handle_team_win(self.team2)

    def _ai_team_turn(self):
        self._team_turn(self.team2, self.team1, self._ai_choose)

    def _team_turn(self, attacking_team: Team, defending_team: Team, choose_action: Callable[[character.Character, AbstractUserInterface, Callable[[TargetOption], None]], None]):
        if attacking_team.isDefeated():
            return

        messages = []
        messages.extend(attacking_team.updateMembersRemaining())
        self.weather.applyEffect(attacking_team.membersRemaining, messages)
        messages.extend(attacking_team.updateMembersRemaining())

        for member in attacking_team.membersRemaining:
            options = member.getActiveChoices()
            if len(options) == 0:
                messages.append(f'{member.name} has no valid targets!')
            else:
                self._pages.display_start_of_character_turn(member, attacking_team, defending_team, messages)
                # todo also need to show details from previous screen
                screen = self._pages.set_up_screen_for_turn(attacking_team, defending_team, messages)
                choose_action(member, screen, lambda to: self._handle_choice(screen, member, attacking_team, defending_team, to)) # need to await this

    def _handle_choice(self, screen: AbstractUserInterface, whos_turn_it_is: character.Character, attacking_team: Team, defending_team: Team, choice: TargetOption):
        body_rows = []
        choice_message = choice.use()
        body_rows.append(choice_message)
        member_messages = defending_team.updateMembersRemaining()
        body_rows.extend(member_messages)
        screen_NEW = Screen(
            f'{whos_turn_it_is}\'s turn',
            [getTeamDisplayData(attacking_team)],
            [getTeamDisplayData(defending_team)],
            body_rows
        )
        screen.display(screen_NEW)

    def _user_choose(self, character: character.Character, screen: AbstractUserInterface, handle_choice: Callable[[TargetOption], None]):
        screen_NEW = Screen(f'{character}\'s turn')
        screen.display_choice("What active do you wish to use?", ChooseOneOf(character.getActiveChoices(), handle_choice), screen_NEW)

    def _ai_choose(self, character: character.Character, screen: AbstractUserInterface, handle_choice: Callable[[TargetOption], None]):
        choice = reduce(lambda i, j: i if i.totalDamage > j.totalDamage else j, character.getActiveChoices())
        handle_choice(choice)
