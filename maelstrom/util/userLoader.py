


from maelstrom.util.user import User

from maelstrom.loaders.characterLoader import loadItem, loadTeam
from util.serialize import AbstractJsonLoader # old util package



class UserLoader(AbstractJsonLoader):
    def __init__(self):
        super().__init__("users")

    def doLoad(self, asJson: dict)->"User":
        return User(
            name = asJson["name"],
            team = loadTeam(asJson["team"]),
            inventory = [loadItem(item) for item in asJson["inventory"]]
        )
