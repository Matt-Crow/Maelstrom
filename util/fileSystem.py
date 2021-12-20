import os.path
import json
from util.serialize import formatFileName

"""
This file will handle all the file system interfacing
"""
USER_DIR = os.path.abspath("users") # relative to root
DATA_DIR = os.path.abspath("data")
ENEMY_DIR = os.path.join(DATA_DIR, "enemies")
AREA_DIR = os.path.join(DATA_DIR, "areas")

def saveSerializable(serializable: "AbstractJsonSerialable", toDir: str):
    path = os.path.join(toDir, formatFileName(serializable.name))
    with open(path, "w") as file:
        file.write(json.dumps(serializable.toJson()))
