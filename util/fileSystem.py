from character import AbstractCharacter, EnemyCharacter
from teams import AbstractTeam
from area import Area
import os.path
from os import walk

"""
This file will handle all the file system interfacing
"""
USER_DIR = os.path.abspath("users") # relative to root
DATA_DIR = os.path.abspath("data")
ENEMY_DIR = os.path.join(DATA_DIR, "enemies")
AREA_DIR = os.path.join(DATA_DIR, "areas")

"""
Formats an AbstractJsonSerialable's name (or any string for that matter)
into an appropriate file name
"""
def formatFileName(serializableName: str)->str:
    return serializableName.replace(" ", "_") + ".json"
"""
Undoes the formatting from formatFileName
"""
def unFormatFileName(fileName: str)->str:
    return fileName.replace(".json", "").replace("_", " ")



"""
Returns a list of all filenames of JSON files
in the given dir, with the unFormatFileName applied
to each of them.
"""
def getJsonFileList(dirPath: str)->"list<str>":
    ret = []
    ext = []
    for (dirPath, dirNames, fileNames) in walk(dirPath):
        for fileName in fileNames:
            ext = os.path.splitext(fileName)
            if len(ext) >= 2 and ext[1] == ".json":
                ret.append(unFormatFileName(fileName))
    return ret

def getUserList()->"list<str>":
    return getJsonFileList(USER_DIR)
def getEnemyList()->"list<str>":
    return getJsonFileList(ENEMY_DIR)
def getAreaList()->"list<str>":
    return getJsonFileList(AREA_DIR)



def loadSerializable(serializableName: str, fromDir: str, cls: "class")->"AbstractJsonSerialable":
    ret = None
    filePath = os.path.join(fromDir, formatFileName(serializableName))
    if os.path.isfile(filePath):
        ret = cls.deserializeJson(cls.readFile(filePath))
    else:
        raise FileNotFoundError(filePath)
    return ret

def loadUser(userName: str)->"PlayerTeam":
    return loadSerializable(userName, USER_DIR, AbstractTeam)
def loadEnemy(enemyName: str)->"EnemyCharacter":
    return loadSerializable(enemyName, ENEMY_DIR, AbstractCharacter)
def loadArea(areaName: str)->"Area":
    return loadSerializable(areaName, AREA_DIR, Area)



def saveSerializable(serializable: "AbstractJsonSerialable", toDir: str):
    serializable.writeToFile(os.path.join(toDir, formatFileName(serializable.name)))
def saveUser(user: "PlayerTeam"):
    saveSerializable(user, USER_DIR)
def saveEnemy(enemy: "EnemyCharacter"):
    saveSerializable(enemy, ENEMY_DIR)
def saveArea(area: "Area"):
    saveSerializable(area, AREA_DIR)

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
