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

# this should be implemented into each AbstractJsonSerialable
def loadSerializable(serializableName: str, fromDir: str, cls: "class")->"AbstractJsonSerialable":
    ret = None
    filePath = os.path.join(fromDir, formatFileName(serializableName))
    if os.path.isfile(filePath):
        ret = cls.deserializeJson(cls.readFile(filePath))
    else:
        raise FileNotFoundError(filePath)
    return ret

def saveSerializable(serializable: "AbstractJsonSerialable", toDir: str):
    serializable.writeToFile(os.path.join(toDir, formatFileName(serializable.name)))
