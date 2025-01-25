from maelstrom.util.user import User
from maelstrom.loaders.characterLoader import load_team
from maelstrom.util.serialize import AbstractJsonLoader

class UserLoader(AbstractJsonLoader):
    def __init__(self):
        super().__init__("users")

    def doLoad(self, asJson: dict)->"User":
        return User(
            name = asJson["name"],
            team = load_team(asJson["team"]),
            inventory = []
        )
