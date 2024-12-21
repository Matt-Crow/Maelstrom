"""
This module handles combat gameplay. This separates the data classes from the
functions that act on their data, preventing classes from become cumbersome
"""



from maelstrom.campaign.level import Level
from maelstrom.dataClasses import character
from maelstrom.dataClasses.team import Team
from maelstrom.dataClasses.weather import WEATHERS, Weather
from maelstrom.loaders.characterLoader import EnemyLoader
from maelstrom.inputOutput.output import debug
from maelstrom.inputOutput.screens import Screen
from maelstrom.inputOutput.teamDisplay import getTeamDisplayData

import random

from maelstrom.util.user import User



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


    screen = Screen()
    screen.setTitle(f'{playerTeam.name} VS. {enemyTeam.name}')
    playerTeamData = getTeamDisplayData(playerTeam)
    enemyTeamData = getTeamDisplayData(enemyTeam)
    screen.addSplitRow(playerTeamData, enemyTeamData)
    screen.addBodyRow(level.prescript)
    screen.addBodyRow(weather.getMsg())
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

    screen = Screen()
    screen.setTitle(f'{playerTeam.name} VS. {enemyTeam.name}')
    screen.addBodyRows(msgs)
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

    def teamTurn(self, attacker, defender, chooseAction: "function(Screen, character.Character)"):
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
        screen = Screen()
        screen.setTitle(f'{character}\'s turn')
        screen.addSplitRow(
            getTeamDisplayData(attackerTeam),
            getTeamDisplayData(defenderTeam)
        )
        screen.addBodyRows(msgs)

        options = character.getActiveChoices()
        if len(options) == 0:
            screen.addBodyRow(f'{character.name} has no valid targets!')
        else: # let them choose their active and target
            choice = chooseAction(screen, character)

            screen.clearBody()
            screen.clearOptions() # prevents a bug where the screen wouldn't display
            msgs.append(choice.use())
            msgs.extend(defenderTeam.updateMembersRemaining())
            screen.addSplitRow(
                getTeamDisplayData(attackerTeam),
                getTeamDisplayData(defenderTeam)
            )
            screen.addBodyRows(msgs)
        screen.display()

    def userChoose(self, screen, character):
        for option in character.getActiveChoices():
            screen.addOption(option)
        return screen.displayAndChoose("What active do you wish to use?")

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
