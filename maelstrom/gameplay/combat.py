"""
This module handles combat gameplay. This separates the data classes from the
functions that act on their data, preventing classes from become cumbersome
"""

from functools import reduce
from maelstrom.campaign.level import Level
from maelstrom.dataClasses.character import Character
from maelstrom.dataClasses.activeAbilities import TargetOption
from maelstrom.dataClasses.team import Team, User
from maelstrom.dataClasses.weather import WEATHERS, Weather
from maelstrom.loaders.character_loader import EnemyLoader
from maelstrom.ui import AbstractUserInterface, Choice, Screen
from maelstrom.util.stringUtil import lengthOfLongest

import random

async def play_level(ui: AbstractUserInterface, level: Level, user: User, enemyLoader: EnemyLoader):
    """
    used to start and run a Level
    """

    enemies = [enemyLoader.load(enemyName) for enemyName in level.enemy_names]
    for enemy in enemies:
        enemy.level = level.enemy_level
    enemy_team = Team("Enemy Team", enemies)
    enemy_team.init_for_battle()

    player_team = user.team
    player_team.init_for_battle()

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
    await ui.display_and_choose(screen) 

    await Encounter(ui, level, player_team, enemy_team, weather).run()

class Encounter:
    """
    An encounter handles team versus team conflict.
    """

    def __init__(self, ui: AbstractUserInterface, level: Level, player_team: Team, enemy_team: Team, weather: Weather):
        self._ui = ui
        self._level = level
        self._player_team = player_team
        self._enemy_team = enemy_team
        self._weather = weather

    async def run(self):
        """
        Runs the encounter until one team wins
        """

        self._player_team.enemyTeam = self._enemy_team
        self._enemy_team.enemyTeam = self._player_team
        self._player_team.init_for_battle()
        self._enemy_team.init_for_battle()
        
        while not self._is_over():
            await self._team_turn(self._enemy_team, self._player_team)
            await self._team_turn(self._player_team, self._enemy_team)

        self._player_team.enemyTeam = None
        self._enemy_team.enemyTeam = None

    def _is_over(self) -> bool:
        return self._player_team.is_defeated() or self._enemy_team.is_defeated()

    async def _team_turn(self, attacking_team: Team, defending_team: Team):
        if attacking_team.is_defeated():
            return

        messages = []
        messages.extend(attacking_team.update_members_remaining())
        self._weather.applyEffect(attacking_team.members_remaining, messages)
        messages.extend(attacking_team.update_members_remaining())

        for member in attacking_team.members_remaining:
            options = member.get_target_options()
            if len(options) == 0:
                messages.append(f'{member.name} has no valid targets!')
            
            screen = Screen(
                f'{member}\'s turn',
                _get_scoreboard_for_team(attacking_team),
                _get_scoreboard_for_team(defending_team),
                body_rows=messages
            )
            await self._ui.display_and_choose(screen) 

            if len(options) != 0:
                choice = None
                if attacking_team is self._player_team:
                    screen.choice = Choice("Choose an active and target:", options)
                    choice = await self._ui.display_and_choose(screen)
                else:
                    screen.choice = None
                    choice = reduce(lambda i, j: i if i.total_damage > j.total_damage else j, options)
                await self._handle_choice(screen, attacking_team, defending_team, choice)
        
            if attacking_team.enemyTeam.is_defeated():
                await self._handle_team_win(attacking_team)
                return # stop, stop, stop, he's already dead!
        
        # once we're done with each member remaining, raise the end of turn event
        attacking_team.turn_end()

    async def _handle_choice(self, screen: Screen, attacking_team: Team, defending_team: Team, choice: TargetOption):
        screen.choice = None
        
        choice_messages = choice.use()
        screen.body_rows.extend(choice_messages)
        member_messages = defending_team.update_members_remaining()
        screen.body_rows.extend(member_messages)

        # replace old scoreboards
        screen.left_scoreboard = _get_scoreboard_for_team(attacking_team)
        screen.right_scoreboard = _get_scoreboard_for_team(defending_team)

        await self._ui.display_and_choose(screen) 

    async def _handle_team_win(self, winner: Team):
        messages = []
        if self._player_team is winner:
            messages.append(f'{self._player_team.name} won!')
            messages.append(self._level.postscript)
        else:
            messages.append("Regretably, you have not won this day. Though someday, you will grow strong enough to overcome this challenge...")
        xp = self._enemy_team.get_xp_given()
        for member in self._player_team.members:
            messages.extend(member.gain_xp(xp))

        screen = Screen(
            title=f'{self._player_team.name} vs {self._enemy_team.name}',
            body_rows=messages
        )
        await self._ui.display_and_choose(screen)

def _get_scoreboard_for_team(team: Team) -> list[str]:
    rows = [
        team.name
    ]
    longest_name = lengthOfLongest((m.name for m in team.members_remaining))
    longest_status = lengthOfLongest((_get_scoreboard_status(m) for m in team.members_remaining))
    for m in team.members_remaining:
        status = _get_scoreboard_status(m)
        row = f'* {m.name.ljust(longest_name)}: {status.rjust(longest_status)}'
        rows.append(row)
    return rows
    
def _get_scoreboard_status(character: Character) -> str:
    return f'{str(character.remaining_hp)} HP / {str(character.energy)} energy'