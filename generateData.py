from character import AbstractCharacter, EnemyCharacter, ENEMY_DIRECTORY
import json



#this file is for management purposes ONLY.
#use it if the data in files gets corrupted or needs to be reset

# TODO: make this write most of the data to a file (files?)
"""
Generates the default data for enemies,
and outputs it to the enemy directory.
"""
def generateEnemies():
    lightning = EnemyCharacter(
        name="Lightning Entity",
        element="lightning",
        stats={
            "energy" : 10,
            "resistance" : -10
        }
    )
    #lightning.displayData()
    lightning.save()

    rain = EnemyCharacter(
        name="Rain Entity",
        element="rain",
        stats={
            "potency" : 10,
            "control" : -10
        }
    )
    #rain.displayData()
    rain.save()

    hail = EnemyCharacter(
        name="Hail Entity",
        element = "hail",
        stats={
            "resistance" : 10,
            "luck" : -10
        }
    )
    #hail.displayData()
    hail.save()

    wind = EnemyCharacter(
        name="Wind Entity",
        element = "wind",
        stats={
            "luck" : 10,
            "potency" : -10
        }
    )
    #wind.displayData()
    wind.save()

    stone = EnemyCharacter(
        name="Stone Soldier",
        element="stone",
        stats={
            "control":5,
            "resistance":10,
            "luck":-5,
            "energy":-5,
            "potency":-5
        }
    )
    #stone.displayData()
    stone.save()
