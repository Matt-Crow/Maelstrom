"""
Battle's responsibilities are mostly being phased into combat.py, but I'll keep
it as a data class later.
"""



from maelstrom.dataClasses.team import Team
from maelstrom.gameplay.combat import Encounter
from maelstrom.inputOutput.teamDisplay import getTeamDisplayData

from battle.weather import WEATHERS, NO_WEATHER
from maelstrom.loaders.characterLoader import EnemyLoader
from util.serialize import AbstractJsonSerialable
from util.stringUtil import entab
from maelstrom.inputOutput.screens import Screen
import random


"""
The Battle class pits 2 teams
against each other,
initializing them
and the weather.
"""
class Battle(AbstractJsonSerialable):
    """
    Required kwargs:
    - name : str
    - desc : str
    - prescript : list of str, defaults to []
    - postscript : list of str, defaults to []
    - forecast : list of Weather, defaults to WEATHERS, or if an empty list is passed, defaults to NO_WEATHER
    - enemyNames : list of str, the names of enemies to put on the enemy team
    - level : the level of enemies on the enemy team
    - rewards : list of Items, defaults to []
    """
    def __init__(self, **kwargs):#name: str, desc: str, script: list, finalAct: list, level: int, enemyNames: list, rewards = []):
        super(Battle, self).__init__(**dict(kwargs, type="Battle"))
        self.name = kwargs["name"]
        self.desc = kwargs["desc"]
        self.prescript = kwargs.get("prescript", [])
        self.postscript = kwargs.get("postscript", [])
        self.forecast = kwargs.get("forecast", WEATHERS)
        if len(self.forecast) == 0:
            self.forecast = [NO_WEATHER]
        self.enemyNames = kwargs["enemyNames"]
        self.level = kwargs["level"]
        self.rewards = kwargs.get("rewards", [])

        self.addSerializedAttributes(
            "name",
            "desc",
            "prescript",
            "postscript",
            "forecast",
            "enemyNames",
            "level",
            "rewards"
        )
        self.enemyLoader = EnemyLoader()

    def getDisplayData(self)->str:
        ret = [
            self.name,
            entab(self.desc)
        ]

        for name in self.enemyNames: # enemy team is not yet loaded
            ret.append(entab("* {0} Lv. {1}".format(name, self.level)))

        return "\n".join(ret)

    def __str__(self):
        return self.getDisplayData()

    """
    Used to start and run the battle
    """
    def play(self, user: "User"):
        enemies = [self.enemyLoader.load(enemyName) for enemyName in self.enemyNames]
        for enemy in enemies:
            enemy.level = self.level
        enemyTeam = Team(
            name="Enemy Team",
            members=enemies
        )

        playerTeam = user.team
        playerTeam.initForBattle()
        enemyTeam.initForBattle()
        self.player_team = playerTeam
        self.enemy_team = enemyTeam
        self.weather = random.choice(self.forecast)
        self.displayIntro()

        msgs = []

        if Encounter(
            playerTeam,
            enemyTeam,
            self.weather
        ).resolve():
            msgs.append(f'{self.player_team.name} won!')
            msgs.extend(self.postscript)

            for reward in self.rewards:
                user.acquire(reward)
        else:
            msgs.append("Regretably, you have not won this day. Though someday, you will grow strong enough to overcome this challenge...")

        xp = self.enemy_team.getXpGiven()
        for member in self.player_team.members:
            msgs.extend(member.gainXp(xp))

        self.displayEnd(msgs)

    """
    Displays the introduction to this Battle
    """
    def displayIntro(self):
        screen = Screen()
        screen.setTitle(f'{self.player_team.name} VS. {self.enemy_team.name}')
        playerTeamData = getTeamDisplayData(self.player_team)
        enemyTeamData = getTeamDisplayData(self.enemy_team)
        screen.addSplitRow(playerTeamData, enemyTeamData)
        screen.addBodyRows(self.prescript)
        screen.addBodyRow(self.weather.getMsg())
        screen.display()

    def displayEnd(self, msgs):
        screen = Screen()
        screen.setTitle(f'{self.player_team.name} VS. {self.enemy_team.name}')
        screen.addBodyRow(self.getDisplayData())
        screen.addBodyRows(msgs)
        screen.display()
