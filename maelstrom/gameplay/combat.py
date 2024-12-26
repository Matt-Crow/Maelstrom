"""
This module handles combat gameplay. This separates the data classes from the
functions that act on their data, preventing classes from become cumbersome
"""

from functools import reduce
from typing import Callable
from maelstrom.campaign.level import Level
from maelstrom.dataClasses import character
from maelstrom.dataClasses.activeAbilities import TargetOption
from maelstrom.dataClasses.team import Team
from maelstrom.dataClasses.weather import WEATHERS, Weather
from maelstrom.loaders.characterLoader import EnemyLoader
from maelstrom.inputOutput.screens import Screen
from maelstrom.pages import Pages
from maelstrom.util.user import User

import random

def playLevel(level: "Level", user: User, enemyLoader: EnemyLoader):
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

    msgs = []

    if Encounter(
        playerTeam,
        enemyTeam,
        weather
    ).resolve():
        msgs.append(f'{playerTeam.name} won!')
        msgs.append(level.postscript)
        # add rewards later
    else:
        msgs.append("Regretably, you have not won this day. Though someday, you will grow strong enough to overcome this challenge...")

    xp = enemyTeam.getXpGiven()
    for member in playerTeam.members:
        msgs.extend(member.gainXp(xp))

    Pages().display_encounter_end(f'{playerTeam.name} VS. {enemyTeam.name}', msgs)

class Encounter:
    """
    An encounter handles team versus team conflict.
    """
    def __init__(self, team1: "Team", team2: "Team", weather: Weather):
        self.team1 = team1
        self.team2 = team2
        self.weather = weather

    def resolve(self) -> bool:
        """
        runs the encounter. Returns True if team1 wins
        """
        self.team1.enemyTeam = self.team2
        self.team2.enemyTeam = self.team1
        self.team1.initForBattle()
        self.team2.initForBattle()

        while not self._is_over():
            self.teamTurn(self.team2, self.team1, self.aiChoose)
            self.teamTurn(self.team1, self.team2, self.userChoose)

        self.team1.enemyTeam = None
        self.team2.enemyTeam = None

        return self.team2.isDefeated()

    def _is_over(self) -> bool:
        return self.team1.isDefeated() or self.team2.isDefeated()

    def teamTurn(self, attacker, defender, chooseAction: Callable[[character.Character, Screen], TargetOption]):
        pages = Pages()
        if attacker.isDefeated():
            return

        msgs = []

        msgs.extend(attacker.updateMembersRemaining())
        self.weather.applyEffect(attacker.membersRemaining, msgs)
        msgs.extend(attacker.updateMembersRemaining())

        for member in attacker.membersRemaining:
            options = member.getActiveChoices()
            if len(options) == 0:
                msgs.append(f'{member.name} has no valid targets!')
            else:
                pages.display_and_choose_combat_action(member, attacker, defender, msgs, chooseAction)

    def userChoose(self, character, screen):
        return screen.display_and_choose_OLD("What active do you wish to use?", character.getActiveChoices())

    def aiChoose(self, character, screen):
        return reduce(lambda i, j: i if i.totalDamage > j.totalDamage else j, character.getActiveChoices())