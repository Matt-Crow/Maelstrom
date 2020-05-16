from utilities import *
from item import Item
from weather import WEATHERS, NO_WEATHER, deserializeWeather
from teams import EnemyTeam
from output import Op
from character import EnemyCharacter, ENEMY_CACHE
from serialize import AbstractJsonSerialable
import random

"""
The Battle class pits 2 teams
against eachother,
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

    Not sure how I want to pass enemies.
    Sending an enemyteam makes sense,
    but is less memory efficient than creating one upon starting the battle.
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

        #self.level = level #the level of enemies

        #self.enemy_team = EnemyTeam(enemyNames, level)

        self.rewards = to_list(rewards)

        self.addSerializedAttributes(
            "name",
            "desc",
            "prescript",
            "postscript",
            "forecast"
        )


    @staticmethod
    def loadJson(jdict: dict) -> "Battle":
        jdict["forecast"] = [deserializeWeather(data) for data in jdict["forecast"]]
        jdict["rewards"] = [Item.read_json(data) for data in jdict["rewards"]]
        return Battle(dict)

    def getDisplayData(self):
        """
        gets data for outputting
        """
        ret = [self.name, "\t" + self.desc]
        for member in self.enemy_team.members:
            ret.append("\t* " + member.getShortDesc())
        return ret

    def __str__(self):
        return self.name

    def load_team(self, team):
        """
        Load the player's team
        """
        self.player_team = team

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

    def begin(self):
        """
        Prepare both teams
        for the match.
        """
        for line in self.prescript:
            Op.add(line)
            Op.display()

        self.enemy_team.initForBattle()
        self.enemy_team.enemy = self.player_team

        self.player_team.initForBattle()
        self.player_team.enemy = self.enemy_team

        self.enemy_team.displayData()
        self.player_team.displayData()

        self.weather = random.choice(self.forecast)
        Op.add(self.weather.getMsg())
        Op.display()

    def end(self):
        """
        The stuff that takes place after battle
        """
        xp = self.enemy_team.getXpGiven()
        for member in self.player_team.members:
            member.gainXp(xp)

    def play(self):
        """
        Used to start
        the battle
        """
        self.begin()

        while not self.enemy_team.isDefeated() and not self.player_team.isDefeated():
            self.weather.applyEffect(self.enemy_team.membersRem)
            # did the weather defeat them?
            if not self.enemy_team.isDefeated():
                self.enemy_team.doTurn()
                # only bother doing player turn if enemy survives
                # so this way we don't get 'ghost rounds'
                self.weather.applyEffect(self.player_team.membersRem)
                if not self.player_team.isDefeated():
                    self.player_team.doTurn()
        self.check_winner()
        self.end()

    """
    Creates a random level
    """
    @staticmethod
    def generateRandom():
        enemyNames = []
        numEnemies = random.randint(1, 4)

        EnemyCharacter.load_enemy(all=True)

        keys = list(ENEMY_CACHE.keys())
        for i in range(0, numEnemies):
            enemyNames.append(random.choice(keys))

        return Battle("Random encounter", enemyNames, 1)
