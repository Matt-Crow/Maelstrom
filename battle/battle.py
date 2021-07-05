from utilities import *
from item import Item
from weather import WEATHERS, NO_WEATHER, Weather
from teams import EnemyTeam
from util.output import Op
from character import EnemyCharacter
from fileSystem import getEnemyList
from serialize import AbstractJsonSerialable
from util.stringUtil import entab
from inputOutput.screens import displayBattleStart, displayTeam, displayBattleEnemyTurn
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


    @classmethod
    def deserializeJson(cls, jdict: dict)->"Battle":
        jdict["forecast"] = [Weather.deserializeJson(data) for data in jdict["forecast"]]
        jdict["rewards"] = [Item.deserializeJson(data) for data in jdict["rewards"]]
        return Battle(**jdict)

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
    Used to start
    the battle
    """
    def play(self, playerTeam):
        # set teams
        self.player_team = playerTeam
        enemies = [EnemyCharacter.loadEnemy(enemyName) for enemyName in self.enemyNames]
        for enemy in enemies:
            enemy.level = self.level
        self.enemy_team = EnemyTeam(
            name="Enemy Team",
            members=enemies
        )

        self.enemy_team.initForBattle()
        self.enemy_team.enemy = self.player_team

        self.player_team.initForBattle()
        self.player_team.enemy = self.enemy_team

        self.weather = random.choice(self.forecast)

        displayTeam(self.enemy_team)
        displayBattleStart(self)

        while not self.enemy_team.isDefeated() and not self.player_team.isDefeated():
            weatherMsg = self.weather.applyEffect(self.enemy_team.membersRem)
            # did the weather defeat them?
            if not self.enemy_team.isDefeated():
                self.enemy_team.doTurn()
                displayBattleEnemyTurn(self, [weatherMsg])
                # only bother doing player turn if enemy survives
                # so this way we don't get 'ghost rounds'
                self.weather.applyEffect(self.player_team.membersRem)
                if not self.player_team.isDefeated():
                    self.player_team.doTurn()
        self.check_winner()
        self.end()

        self.enemy_team = None # uncache enemy team to save memory

    # add random loot
    def check_winner(self):
        """
        Runs when one
        teams loses all
        members.
        """
        if not self.player_team.isDefeated():
            Op.add(self.player_team.name + " won!")
            Op.display()

            for line in self.postscript:
                Op.add(line)
                Op.display()

            for reward in self.rewards:
                if reward != None:
                    reward.give(self.player_team)

    def end(self):
        """
        The stuff that takes place after battle
        """
        xp = self.enemy_team.getXpGiven()
        for member in self.player_team.members:
            member.gainXp(xp)

    """
    Creates a random level
    """
    @staticmethod
    def generateRandom():
        enemyNames = []
        numEnemies = random.randint(1, 4)

        allEnemyNames = getEnemyList()

        for i in range(0, numEnemies):
            enemyNames.append(random.choice(allEnemyNames))

        return Battle(
            name="Random encounter",
            desc="Random battle",
            enemyNames=enemyNames,
            level=1
        )
