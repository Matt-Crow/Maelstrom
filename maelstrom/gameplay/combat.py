"""
This module handles combat gameplay. This separates the data classes from the
functions that act on their data, preventing classes from become cumbersome
"""

from functools import reduce
from maelstrom.campaign.level import Level
from maelstrom.choices import ChooseOneOf
from maelstrom.dataClasses.character import Character
from maelstrom.dataClasses.activeAbilities import TargetOption
from maelstrom.dataClasses.team import Team
from maelstrom.dataClasses.weather import WEATHERS, Weather
from maelstrom.loaders.characterLoader import EnemyLoader
from maelstrom.ui import AbstractUserInterface, Screen
from maelstrom.util.stringUtil import lengthOfLongest
from maelstrom.util.user import User

import random

def play_level(ui: AbstractUserInterface, level: Level, user: User, enemyLoader: EnemyLoader):
    """
    used to start and run a Level
    """

    enemies = [enemyLoader.load(enemyName) for enemyName in level.enemy_names]
    for enemy in enemies:
        enemy.level = level.enemy_level
    enemy_team = Team(name="Enemy Team", members=enemies)
    enemy_team.initForBattle()

    player_team = user.team
    player_team.initForBattle()

    weather = random.choice(WEATHERS)
    
    # display start of encounter
    body_messages = []
    if len(level.prescript) > 0:
        body_messages.append(level.prescript)
    if len(weather.getMsg()) > 0:
        body_messages.append(weather.getMsg())
    
    screen = Screen(
        f'{player_team.name} vs {enemy_team.name}',
        _get_scoreboard_for_team(player_team),
        _get_scoreboard_for_team(enemy_team),
        body_messages
    )
    ui.display(screen)

    Encounter(ui, level, player_team, enemy_team, weather).run()

class Encounter:
    """
    An encounter handles team versus team conflict.
    """

    def __init__(self, ui: AbstractUserInterface, level: Level, player_team: Team, enemy_team: Team, weather: Weather):
        self._ui = ui
        self.level = level
        self.player_team = player_team
        self.enemy_team = enemy_team
        self.weather = weather

    def run(self):
        """
        Runs the encounter until one team wins
        """
        self.player_team.enemyTeam = self.enemy_team
        self.enemy_team.enemyTeam = self.player_team
        self.player_team.initForBattle()
        self.enemy_team.initForBattle()
        
        while not self._is_over():
            self._player_team_turn() # recursively calls enemy team turn

        self.player_team.enemyTeam = None
        self.enemy_team.enemyTeam = None

    def _is_over(self) -> bool:
        return self.player_team.isDefeated() or self.enemy_team.isDefeated()

    def _player_team_turn(self):
        self._team_turn(self.player_team, self.enemy_team)

        if self.enemy_team.isDefeated():
            self._handle_team_win(self.player_team)
            return
        
        self._ai_team_turn()
        if self.player_team.isDefeated():
            self._handle_team_win(self.enemy_team)

    def _ai_team_turn(self):
        self._team_turn(self.enemy_team, self.player_team)

    def _team_turn(self, attacking_team: Team, defending_team: Team):
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
            
            screen = Screen(
                f'{member}\'s turn',
                _get_scoreboard_for_team(attacking_team),
                _get_scoreboard_for_team(defending_team),
                body_rows=messages
            )
            self._ui.display(screen)

            if len(options) != 0:
                if attacking_team is self.player_team:
                    screen.choice = ChooseOneOf("Choose an active and target:", options, lambda to: self._handle_choice(screen, attacking_team, defending_team, to))
                    self._ui.display(screen)
                else:
                    choice = reduce(lambda i, j: i if i.totalDamage > j.totalDamage else j, options)
                    self._handle_choice(screen, attacking_team, defending_team, choice)

    def _handle_choice(self, screen: Screen, attacking_team: Team, defending_team: Team, choice: TargetOption):
        screen.choice = None
        
        choice_message = choice.use()
        screen.body_rows.append(choice_message)
        member_messages = defending_team.updateMembersRemaining()
        screen.body_rows.extend(member_messages)

        # replace old scoreboards
        screen.left_scoreboard = _get_scoreboard_for_team(attacking_team)
        screen.right_scoreboard = _get_scoreboard_for_team(defending_team)

        self._ui.display(screen)

    def _handle_team_win(self, winner: Team):
        messages = []
        if self.player_team is winner:
            messages.append(f'{self.player_team.name} won!')
            messages.append(self.level.postscript)
        else:
            messages.append("Regretably, you have not won this day. Though someday, you will grow strong enough to overcome this challenge...")
        xp = self.enemy_team.getXpGiven()
        for member in self.player_team.members:
            messages.extend(member.gainXp(xp))

        screen = Screen(
            title=f'{self.player_team.name} vs {self.enemy_team.name}',
            body_rows=messages
        )
        self._ui.display(screen)

def _get_scoreboard_for_team(team: Team) -> list[str]:
    rows = [
        team.name
    ]
    longest_name = lengthOfLongest((m.name for m in team.membersRemaining))
    longest_status = lengthOfLongest((_get_scoreboard_status(m) for m in team.membersRemaining))
    for m in team.membersRemaining:
        status = _get_scoreboard_status(m)
        row = f'* {m.name.ljust(longest_name)}: {status.rjust(longest_status)}'
        rows.append(row)
    return rows
    
def _get_scoreboard_status(character: Character) -> str:
    return f'{str(character.remHp)} HP / {str(character.energy)} energy'