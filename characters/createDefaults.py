"""
This module handles creating the default instances for character-related classes.
This helps circumvent several circular-dependency issues, and abstractifies the
object creation process a bit.
"""



from maelstrom.dataClasses.activeAbilities import createDefaultActives
from maelstrom.dataClasses.passiveAbilities import getPassiveAbilityList
from battle.area import Area, Location
from battle.battle import Battle
from characters.character import EnemyCharacter, PlayerCharacter
from characters.characterLoader import EnemyLoader
from characters.item import Item
import random



NEXT_ITEM_NUM = 1 # I don't like globals, but need this for now



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
        desc="No description",
        locations=[createDefaultLocation()],
        levels=[createRandomBattle()]
    )

def createRandomBattle()->"Battle":
    enemyNames = []
    numEnemies = random.randint(1, 4)
    allEnemyNames = EnemyLoader().getOptions()

    for i in range(numEnemies):
        enemyNames.append(random.choice(allEnemyNames))

    return Battle(
        name="Random encounter",
        desc="Random battle",
        enemyNames=enemyNames,
        level=1,
        rewards=[createRandomItem()]
    )

def createDefaultLocation():
    return Location(
        name="Shoreline",
        desc="Gentle waves lap at the shore.",
        script=[
            "I'm not sure how I feel about the sand...",
            "is it course and rough?",
            "or soft?"
        ]
    )

def createDefaultPlayer(name, element)->"PlayerCharacter":
    return PlayerCharacter(
        name=name,
        element=element,
        actives=createDefaultActives(element),
        passives=createDefaultPassives()
    )

def createDefaultPassives()->"List<AbstractPassive>":
    return [p.copy() for p in getPassiveAbilityList()]

def createRandomItem()->"Item":
    global NEXT_ITEM_NUM
    name = f'Random Item #{NEXT_ITEM_NUM}'
    NEXT_ITEM_NUM += 1
    return Item(name=name)

def createDefaultEnemies():
    enemies = []

    enemies.append(EnemyCharacter(
        name="Lightning Entity",
        element="lightning",
        stats={
            "energy" : 10,
            "resistance" : -10
        },
        actives=createDefaultActives("lightning"),
        passives=createDefaultPassives() # each needs their own copy
    ))

    enemies.append(EnemyCharacter(
        name="Rain Entity",
        element="rain",
        stats={
            "potency" : 10,
            "control" : -10
        },
        actives=createDefaultActives("rain"),
        passives=createDefaultPassives()
    ))

    enemies.append(EnemyCharacter(
        name="Hail Entity",
        element = "hail",
        stats={
            "resistance" : 10,
            "luck" : -10
        },
        actives=createDefaultActives("hail"),
        passives=createDefaultPassives()
    ))

    enemies.append(EnemyCharacter(
        name="Wind Entity",
        element = "wind",
        stats={
            "luck" : 10,
            "potency" : -10
        },
        actives=createDefaultActives("wind"),
        passives=createDefaultPassives()
    ))

    enemies.append(EnemyCharacter(
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
