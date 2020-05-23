from character import AbstractCharacter, EnemyCharacter
from teams import AbstractTeam
import os.path
from os import walk

"""
This file will handle all the file system interfacing
"""
USER_DIR = os.path.abspath("users") # relative to root
DATA_DIR = os.path.abspath("data")
ENEMY_DIR = os.path.join(DATA_DIR, "enemies")

def getUserList()->"list<str>":
    ret = []
    for (dirPath, dirNames, fileNames) in walk(USER_DIR):
        ret.extend([fileName.replace(".json", "").replace("_", " ") for fileName in fileNames])
    return ret
def getEnemyList()->"list<str>":
    ret = []
    for (dirPath, dirNames, fileNames) in walk(ENEMY_DIR):
        ret.extend([fileName.replace(".json", "").replace("_", " ") for fileName in fileNames])
    return ret

def loadUser(userName: str)->"PlayerTeam":
    filePath = os.path.join(USER_DIR, userName.replace(" ", "_")) + ".json"
    ret = None
    if os.path.isfile(filePath):
        ret = AbstractTeam.deserializeJson(AbstractTeam.readFile(filePath))
    else:
        raise FileNotFoundError(filePath)
    return ret

def loadEnemy(enemyName: str)->"EnemyCharacter":
    filePath = os.path.join(ENEMY_DIR, enemyName.replace(" ", "_")) + ".json"
    ret = None
    if os.path.isfile(filePath):
        ret = AbstractCharacter.deserializeJson(AbstractCharacter.readFile(filePath))
    else:
        raise FileNotFoundError(filePath)
    return ret

def saveUser(user: "PlayerTeam"):
    user.writeToFile(os.path.join(USER_DIR, user.name.replace(" ", "_")) + ".json")

def saveEnemy(enemy: "EnemyCharacter"):
    enemy.writeToFile(os.path.join(ENEMY_DIR, enemy.name.replace(" ", "_")) + ".json")

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
    saveEnemy(lightning)

    rain = EnemyCharacter(
        name="Rain Entity",
        element="rain",
        stats={
            "potency" : 10,
            "control" : -10
        }
    )
    #rain.displayData()
    saveEnemy(rain)

    hail = EnemyCharacter(
        name="Hail Entity",
        element = "hail",
        stats={
            "resistance" : 10,
            "luck" : -10
        }
    )
    #hail.displayData()
    saveEnemy(hail)

    wind = EnemyCharacter(
        name="Wind Entity",
        element = "wind",
        stats={
            "luck" : 10,
            "potency" : -10
        }
    )
    #wind.displayData()
    saveEnemy(wind)

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
    saveEnemy(stone)
