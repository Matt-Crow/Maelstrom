"""
This module handles the conversion of JSON files of player characters into
Character objects in the program
"""



from util.serialize import AbstractJsonLoader
from actives.actives import AbstractActive, MeleeAttack
from passives import AbstractPassive, Threshhold, OnHitGiven, OnHitTaken
from item import Item
from character import PlayerCharacter, EnemyCharacter
from battle.teams import PlayerTeam



class PlayerTeamLoader(AbstractJsonLoader):
    def __init__(self):
        super().__init__("users")

    def doLoad(self, asJson: dict)->"PlayerTeam":
        return loadTeam(asJson)

class EnemyLoader(AbstractJsonLoader):
    def __init__(self):
        super().__init__("data.enemies")

    def doLoad(self, asJson: dict)->"EnemyCharacter":
        return loadCharacter(asJson)



"""
These types of objects are not stored in a directory, so don't subclass
AbstractJsonLoader for them.
"""

def loadTeam(asJson: dict)->"AbstractTeam":
    type = asJson["type"]
    ret = None
    if type == "PlayerTeam":
        asJson["member"] = loadCharacter(asJson["members"][0])
        asJson["inventory"] = [loadItem(item) for item in asJson["inventory"]]
        ret = PlayerTeam(**asJson)
    elif type =="EnemyTeam":
        asJson["members"] = [loadCharacter(member) for member in asJson["members"]]
        ret = EnemyTeam(**asJson)
    else:
        raise Error("Type not found for AbstractTeam: {0}".format(type))
    return ret

def loadCharacter(asJson: dict)->"AbstractCharacter":
    asJson = asJson.copy()
    ctype = asJson["type"]
    asJson["actives"] = [loadActive(data) for data in asJson["actives"]]
    asJson["passives"]= [loadPassive(data) for data in asJson["passives"]]
    asJson["equippedItems"] = [loadItem(data) for data in asJson["equippedItems"]]
    ret = None

    if ctype == "PlayerCharacter":
        ret = PlayerCharacter(**asJson)
    elif ctype == "EnemyCharacter":
        ret = EnemyCharacter(**asJson)
    else:
        raise Exception("Type not found! " + ctype)

    return ret

def loadActive(asJson: dict)->"AbstractActive":
    ret = None
    type = asJson["type"]

    if type == "AbstractActive":
        ret = AbstractActive(**asJson)
    elif type == "MeleeAttack":
        ret = MeleeAttack(**asJson)
    else:
        raise Exception("Type not found for AbstractActive: " + type)

    return ret

def loadPassive(asJson: dict)->"AbstractPassive":
    ret = None
    type = asJson["type"]
    if type == "Threshhold Passive":
        ret = Threshhold(**asJson)
    elif type == "On Hit Given Passive":
        ret = OnHitGiven(**asJson)
    elif type == "On Hit Taken Passive":
        ret = OnHitTaken(**asJson)
    else:
        raise Exception("Type not found for AbstractPassive: " + type)
    return ret

def loadItem(asJson: dict)->"Item":
    return Item(**asJson)