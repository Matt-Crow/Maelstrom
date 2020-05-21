import os.path
from os import walk

"""
This file will handle all the file system interfacing
"""
USER_DIR = os.path.abspath("users") # relative to root

def getUserList()->"list<str>":
    ret = []
    for (dirPath, dirNames, fileNames) in walk(USER_DIR):
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

def saveUser(user: "PlayerTeam"):
    user.writeToFile(os.path.join(USER_DIR, user.name.replace(" ", "_")) + ".json")
