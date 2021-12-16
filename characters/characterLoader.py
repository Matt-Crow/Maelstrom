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
        asJson["equippedItems"] = [Item.deserializeJson(data) for data in asJson["equippedItems"]]
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
        asJson = asJson.copy()
        asJson["member"] = self.characterLoader.doLoad(asJson["members"][0])
        asJson["inventory"] = [Item.deserializeJson(item) for item in asJson["inventory"]]
        return PlayerTeam(**asJson)
