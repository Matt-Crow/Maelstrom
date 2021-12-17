"""
This module handles the conversion of JSON files of player characters into
Character objects in the program
"""



from util.loader import AbstractJsonLoader
from actives.actives import AbstractActive
from passives import AbstractPassive
from item import Item
from character import PlayerCharacter, EnemyCharacter
from battle.teams import PlayerTeam



class CharacterLoader(AbstractJsonLoader):

    def __init__(self):
        super().__init__("users") # change maybe

    def doLoad(self, asJson: dict)->"AbstractCharacter":
        asJson = asJson.copy()
        ctype = asJson["type"]
        asJson["actives"] = [AbstractActive.deserializeJson(data) for data in asJson["actives"]]
        asJson["passives"]= [AbstractPassive.deserializeJson(data) for data in asJson["passives"]]
        asJson["equippedItems"] = [loadItem(data) for data in asJson["equippedItems"]]
        ret = None

        if ctype == "PlayerCharacter":
            ret = PlayerCharacter(**asJson)
        elif ctype == "EnemyCharacter":
            ret = EnemyCharacter(**asJson)
        else:
            raise Exception("Type not found! " + ctype)

        return ret

class PlayerTeamLoader(AbstractJsonLoader):
    def __init__(self):
        super().__init__("users")
        self.characterLoader = CharacterLoader()

    def doLoad(self, asJson: dict)->"PlayerTeam":
        return loadTeam(self.characterLoader, asJson)

class EnemyLoader(AbstractJsonLoader):
    def __init__(self):
        super().__init__("data.enemies")
        self.characterLoader = CharacterLoader()

    def doLoad(self, asJson: dict)->"EnemyCharacter":
        return self.characterLoader.doLoad(asJson)

# needs to be kept separate from PlayerTeamLoader, as EnemyTeamLoader also needs this
def loadTeam(characterLoader: "CharacterLoader", asJson: dict)->"AbstractTeam":
    type = asJson["type"]
    ret = None
    if type == "PlayerTeam":
        asJson["member"] = characterLoader.doLoad(asJson["members"][0])
        asJson["inventory"] = [loadItem(item) for item in asJson["inventory"]]
        ret = PlayerTeam(**asJson)
    elif type =="EnemyTeam":
        asJson["members"] = [characterLoader.doLoad(member) for member in asJson["members"]]
        ret = EnemyTeam(**asJson)
    else:
        raise Error("Type not found for AbstractTeam: {0}".format(type))
    return ret

def loadItem(asJson: dict)->"Item":
    return Item(**asJson)
