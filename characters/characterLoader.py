"""
This module handles the conversion of JSON files of player characters into
Character objects in the program
"""



from maelstrom.dataClasses.activeAbilities import getActiveAbilityList
from maelstrom.dataClasses.passiveAbilities import getPassiveAbilityList
from util.serialize import AbstractJsonLoader
from characters.item import Item
from characters.character import PlayerCharacter, EnemyCharacter
from battle.teams import PlayerTeam



NAME_TO_ACTIVE = dict()
for active in getActiveAbilityList():
    NAME_TO_ACTIVE[active.name] = active

NAME_TO_PASSIVE = dict()
for passive in getPassiveAbilityList():
    NAME_TO_PASSIVE[passive.name] = passive



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
    asJson["passives"]= [loadPassive(name) for name in asJson["passives"]]
    asJson["equippedItems"] = [loadItem(data) for data in asJson["equippedItems"]]
    ret = None

    if ctype == "PlayerCharacter":
        ret = PlayerCharacter(**asJson)
    elif ctype == "EnemyCharacter":
        ret = EnemyCharacter(**asJson)
    else:
        raise Exception("Type not found! " + ctype)

    return ret

def loadActive(name: str)->"AbstractActive":
    if name not in NAME_TO_ACTIVE:
        raise Exception(f'no active defined with name "{name}"')
    return NAME_TO_ACTIVE[name]

def loadPassive(name: str)->"AbstractPassive":
    if name not in NAME_TO_PASSIVE:
        raise Exception(f'no passives defined with name "{name}"')
    return NAME_TO_PASSIVE[name]

def loadItem(asJson: dict)->"Item":
    return Item(**asJson)
