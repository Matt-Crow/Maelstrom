"""
This module handles creating the default instances for character-related classes.
This helps circumvent several circular-dependency issues, and abstractifies the
object creation process a bit.
"""



from characters.character import EnemyCharacter
from characters.characterLoader import EnemyLoader



def saveDefaultData():
    """
    Creates all the default
    enemies in the enemy directory
    """
    enemyLoader = EnemyLoader()
    for enemy in createDefaultEnemies():
        enemyLoader.save(enemy)


def createDefaultEnemies():
    enemies = []

    enemies.append(EnemyCharacter(
        name="Lightning Entity",
        element="lightning",
        stats={
            "energy" : 10,
            "resistance" : -10
        }
    ))

    enemies.append(EnemyCharacter(
        name="Rain Entity",
        element="rain",
        stats={
            "potency" : 10,
            "control" : -10
        }
    ))

    enemies.append(EnemyCharacter(
        name="Hail Entity",
        element = "hail",
        stats={
            "resistance" : 10,
            "luck" : -10
        }
    ))

    enemies.append(EnemyCharacter(
        name="Wind Entity",
        element = "wind",
        stats={
            "luck" : 10,
            "potency" : -10
        }
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
        }
    ))

    return enemies
