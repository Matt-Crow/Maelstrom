"""
This module handles creating the default instances for character-related classes.
This helps circumvent several circular-dependency issues, and abstractifies the
object creation process a bit.
"""



from maelstrom.dataClasses.activeAbilities import createDefaultActives
from maelstrom.dataClasses.campaign import Area, Level, Location
from maelstrom.dataClasses.character import Character
from maelstrom.dataClasses.item import getItemList
from maelstrom.dataClasses.passiveAbilities import getPassiveAbilityList
from maelstrom.loaders.characterLoader import EnemyLoader
import random



def saveDefaultData():
    """
    Creates all the default
    enemies in the enemy directory
    """
    enemyLoader = EnemyLoader()
    for enemy in createDefaultEnemies():
        enemyLoader.save(enemy)

def createDefaultArea()->"Area":
    return Area(
        name="Test Area",
        description="No description",
        locations=[createDefaultLocation()],
        levels=[createRandomLevel(i) for i in range(1, 5)]
    )

def createRandomLevel(numEnemies: int)->"Level":
    enemyNames = []
    allEnemyNames = EnemyLoader().getOptions()

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
        passives=createDefaultPassives()
    )

def createDefaultPassives()->"List<AbstractPassive>":
    return [p.copy() for p in getPassiveAbilityList()]

def createRandomItem()->"Item":
    return random.choice(getItemList())

def createDefaultEnemies():
    enemies = []

    enemies.append(Character(
        name="Lightning Entity",
        element="lightning",
        stats={
            "energy" : 10,
            "resistance" : -10
        },
        actives=createDefaultActives("lightning"),
        passives=createDefaultPassives() # each needs their own copy
    ))

    enemies.append(Character(
        name="Rain Entity",
        element="rain",
        stats={
            "potency" : 10,
            "control" : -10
        },
        actives=createDefaultActives("rain"),
        passives=createDefaultPassives()
    ))

    enemies.append(Character(
        name="Hail Entity",
        element = "hail",
        stats={
            "resistance" : 10,
            "luck" : -10
        },
        actives=createDefaultActives("hail"),
        passives=createDefaultPassives()
    ))

    enemies.append(Character(
        name="Wind Entity",
        element = "wind",
        stats={
            "luck" : 10,
            "potency" : -10
        },
        actives=createDefaultActives("wind"),
        passives=createDefaultPassives()
    ))

    enemies.append(Character(
        name="Stone Soldier",
        element="stone",
        stats={
            "control":5,
            "resistance":10,
            "luck":-5,
            "energy":-5,
            "potency":-5
        },
        actives=createDefaultActives("stone"),
        passives=createDefaultPassives()
    ))

    return enemies
