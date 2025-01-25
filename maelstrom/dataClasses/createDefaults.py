"""
This module handles creating the default instances for character-related classes.
This helps circumvent several circular-dependency issues, and abstractifies the
object creation process a bit.
"""

from maelstrom.campaign.level import Level
from maelstrom.dataClasses.activeAbilities import createDefaultActives
from maelstrom.dataClasses.character import Character
from maelstrom.dataClasses.passiveAbilities import getPassiveAbilityList
from maelstrom.loaders.characterLoader import EnemyLoader
import random

# will use this later
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
        enemy_names=enemyNames,
        enemy_level=1
    )

def createDefaultPlayer(name, element)->"Character":
    return Character(
        name=name,
        element=element,
        actives=createDefaultActives(element)
    )

