"""
This module handles combat gameplay. This separates the data classes from the
functions that act on their data, preventing classes from become cumbersome
"""



from typing import Callable
from maelstrom.campaign.level import Level
from maelstrom.dataClasses import character
from maelstrom.dataClasses.team import Team
from maelstrom.dataClasses.weather import WEATHERS, Weather
from maelstrom.loaders.characterLoader import EnemyLoader
from maelstrom.inputOutput.output import debug
from maelstrom.inputOutput.screens import Screen
from maelstrom.util.stringUtil import lengthOfLongest
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


    screen = Screen(f'{playerTeam.name} VS. {enemyTeam.name}')
    playerTeamData = getTeamDisplayData(playerTeam)
    enemyTeamData = getTeamDisplayData(enemyTeam)
    screen.add_split_row(playerTeamData, enemyTeamData)
    screen.add_body_row(level.prescript)
    screen.add_body_row(weather.getMsg())
    screen.display()


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

    screen = Screen(f'{playerTeam.name} VS. {enemyTeam.name}')
    screen.add_body_rows(msgs)
    screen.display()



class Encounter:
    """
    An encounter handles team versus team conflict.
    """
    def __init__(self, team1: "Team", team2: "Team", weather: Weather):
        self.team1 = team1
        self.team2 = team2
        self.weather = weather

    def resolve(self)->bool:
        """
        runs the encounter. Returns True if team1 wins
        """
        self.team1.enemyTeam = self.team2
        self.team2.enemyTeam = self.team1
        self.team1.initForBattle()
        self.team2.initForBattle()

        while not self.isOver():
            self.team2Turn()
            self.team1Turn()

        self.team1.enemyTeam = None
        self.team2.enemyTeam = None

        return self.team2.isDefeated()

    def isOver(self)->bool:
        return self.team1.isDefeated() or self.team2.isDefeated()

    def team1Turn(self):
        self.teamTurn(self.team1, self.team2, self.userChoose)

    def team2Turn(self):
        self.teamTurn(self.team2, self.team1, self.aiChoose)

    def teamTurn(self, attacker, defender, chooseAction: Callable[[Screen, character.Character], any]):
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
                self.characterChoose(attacker, member, defender, chooseAction, msgs)

    def characterChoose(self, attackerTeam, character, defenderTeam, chooseAction, msgs):
        screen = Screen(f'{character}\'s turn')
        screen.add_split_row(
            getTeamDisplayData(attackerTeam),
            getTeamDisplayData(defenderTeam)
        )
        screen.add_body_rows(msgs)

        options = character.getActiveChoices()
        if len(options) == 0:
            screen.add_body_row(f'{character.name} has no valid targets!')
        else: # let them choose their active and target
            choice = chooseAction(screen, character)
            screen.add_body_row(choice.use())
            screen.add_body_rows(defenderTeam.updateMembersRemaining())
        screen.display()

    def userChoose(self, screen, character):
        return screen.display_and_choose("What active do you wish to use?", character.getActiveChoices())

    def aiChoose(self, screen, character):
        choices = character.getActiveChoices()
        if len(choices) == 0:
            return None

        best = choices[0]
        bestDmg = 0
        debug("-" * 10)
        for choice in choices:
            if choice.totalDamage > bestDmg:
                best = choice
                bestDmg = choice.totalDamage
            debug(f'Damage with {choice}: {choice.totalDamage}')
        debug("-" * 10)

        return best

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