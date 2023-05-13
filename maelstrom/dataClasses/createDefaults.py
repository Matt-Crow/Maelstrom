"""
This module handles creating the default instances for character-related classes.
This helps circumvent several circular-dependency issues, and abstractifies the
object creation process a bit.
"""

from maelstrom.dataClasses.activeAbilities import createDefaultActives
from maelstrom.dataClasses.campaign import Area, Level, Location
from maelstrom.dataClasses.character import Character
from maelstrom.dataClasses.passiveAbilities import getPassiveAbilityList
from maelstrom.loaders.characterLoader import EnemyLoader
import random

def createDefaultArea(enemy_loader: EnemyLoader)->"Area":
    return Area(
        name="Test Area",
        description="No description",
        locations=[createDefaultLocation()],
        levels=[createRandomLevel(enemy_loader, i) for i in range(1, 5)]
    )

def createRandomLevel(enemy_loader: EnemyLoader, numEnemies: int)->"Level":
    enemyNames = []
    allEnemyNames = enemy_loader.getOptions()

    for i in range(numEnemies):
        enemyNames.append(random.choice(allEnemyNames))

    return Level(
        name="Random encounter",
        description="Random battle",
        prescript="from out of nowhere... some enemies attack!",
        postscript="the enemies flee before your elemental might",
        enemyNames=enemyNames,
        enemyLevel=1
    )

def createDefaultLocation():
    return Location(
        name="Shoreline",
        description="Gentle waves lap at the shore."
    )

def createDefaultPlayer(name, element)->"Character":
    return Character(
        name=name,
        element=element,
        actives=createDefaultActives(element),
        passives=[p.copy() for p in getPassiveAbilityList()]
    )

