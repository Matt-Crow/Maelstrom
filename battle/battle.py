from utilities import *
from item import Item
from weather import WEATHERS, NO_WEATHER, Weather
from teams import EnemyTeam
from character import EnemyCharacter
from fileSystem import getEnemyList
from serialize import AbstractJsonSerialable
from util.stringUtil import entab
from inputOutput.screens import Screen
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
    Used to start and run the battle
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

        # TODO: add a "scout" option to Area that allows the user to do this
        # but will need to make sure they are initialized
        self.enemy_team.display()

        self.displayIntro()

        while not self.enemy_team.isDefeated() and not self.player_team.isDefeated():
            self.doEnemyTurn()
            if not self.enemy_team.isDefeated():
                # only bother doing player turn if enemy survives
                # so this way we don't get 'ghost rounds'
                self.doPlayerTurn()

        # By now, one team has been eliminated
        self.gameEnd()

        self.enemy_team = None # uncache enemy team to save memory

    """
    Displays the introduction to this Battle
    """
    def displayIntro(self):
        screen = Screen()
        screen.setTitle(f'{self.player_team.name} VS. {self.enemy_team.name}')
        playerTeamData = self.player_team.getShortDisplayData()
        enemyTeamData = self.enemy_team.getShortDisplayData()
        screen.addSplitRow(playerTeamData, enemyTeamData)
        screen.addBodyRows(self.prescript)
        screen.addBodyRow(self.weather.getMsg())
        screen.display()

    """
    This one doesn't display as much as doPlayerTurn, as the player needs to be
    more informed, and there isn't much point to displaying as much for the AI's
    turn
    """
    def doEnemyTurn(self)->"List<str>":
        msgs = []

        # Pre-turn steps
        msgs.extend(self.enemy_team.updateMembersRem()) # check if any were KOed on player turn
        msgs.append(self.weather.applyEffect(self.enemy_team.membersRem)) # yes, this is supposed to be "append", not "extend"
        msgs.extend(self.enemy_team.updateMembersRem()) # check if the weather defeated anyone

        if self.enemy_team.isDefeated():
            # todo add message
            pass
        else:
            # Pre-choose attack steps
            if self.enemy_team.active.isKoed() or self.enemy_team.shouldSwitch():
                msgs.append(self.enemy_team.chooseNewActive())

            # Attack steps
            msgs.append(self.enemy_team.active.chooseActive())

        self.displayEnemyTurn(msgs)

    def displayEnemyTurn(self, msgs: "List<str>"):
        screen = Screen()
        screen.setTitle(f'{self.enemy_team.name}\'s turn')
        playerTeamData = self.player_team.getShortDisplayData()
        enemyTeamData = self.enemy_team.getShortDisplayData()
        screen.addSplitRow(playerTeamData, enemyTeamData)
        screen.addBodyRows(msgs)
        screen.display()

    def doPlayerTurn(self)->"List<str>":
        msgs = []

        # Pre-turn steps
        msgs.extend(self.player_team.updateMembersRem()) # check if any were KOed on player turn
        msgs.append(self.weather.applyEffect(self.player_team.membersRem)) # yes, this is supposed to be "append", not "extend"
        msgs.extend(self.player_team.updateMembersRem()) # check if the weather defeated anyone
        self.displayPlayerTurn(msgs)
        if self.player_team.isDefeated():
            # todo add message
            pass
        else:
            # Pre-choose attack steps
            if self.player_team.shouldSwitch():
                msgs.append(self.player_team.chooseNewActive())
                self.displayPlayerTurn(msgs)

            # Attack steps
            screen = Screen()
            screen.setTitle(f'{self.player_team.active}\'s turn')
            for option in self.player_team.active.getActiveChoices():
                screen.addOption(option)
            active = screen.displayAndChoose("What active do you wish to use?");
            msgs.append(active.use())

        self.displayPlayerTurn(msgs)

    """
    This method is called multiple times to keep the user up to date on what is
    happening
    """
    def displayPlayerTurn(self, msgs):
        screen = Screen()
        screen.setTitle(f'{self.player_team.name}\'s turn')
        playerTeamData = self.player_team.getShortDisplayData()
        enemyTeamData = self.enemy_team.getShortDisplayData()
        screen.addSplitRow(playerTeamData, enemyTeamData)
        screen.addBodyRows(msgs)
        screen.display()

    # add random loot
    """
    The stuff that takes place after battle. Runs when one team loses all
    members.
    """
    def gameEnd(self):
        msgs = []

        if self.player_team.isDefeated():
            msgs.append("Regretably, you have not won this day. Though someday, you will grow strong enough to overcome this challenge...")
        else:
            msgs.append(f'{self.player_team.name} won!')
            msgs.extend(self.postscript)

            for reward in self.rewards:
                if reward != None:
                    reward.give(self.player_team)

        xp = self.enemy_team.getXpGiven()
        for member in self.player_team.members:
            msgs.extend(member.gainXp(xp))

        self.displayEnd(msgs)

    def displayEnd(self, msgs):
        screen = Screen()
        screen.setTitle(f'{self.player_team.name} VS. {self.enemy_team.name}')
        screen.addBodyRow(self.getDisplayData())
        screen.addBodyRows(msgs)
        screen.display()

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
