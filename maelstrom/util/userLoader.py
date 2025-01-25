import json
from os import walk
import os
from maelstrom.util.user import User
from maelstrom.loaders.characterLoader import load_team

class UserLoader:
    def __init__(self):
        self._folder = os.path.abspath("users")

    def get_user_names(self) -> list[str]:
        """
        returns a list of all the possible objects this can retrieve
        """
        ret = []
        ext = []
        for (_, _, file_names) in walk(self._folder):
            for file_name in file_names:
                ext = os.path.splitext(file_name)
                if len(ext) >= 2 and ext[1] == ".json":
                    ret.append(file_name.replace(".json", "").replace("_", " "))
        return ret
    
    def load_user(self, name: str):
        path = self._get_path_by_user_name(name)
        with open(path) as file:
            as_json = json.loads(file.read())
            return User(
                name = as_json["name"],
                team = load_team(as_json["team"]),
                inventory = []
            )
    
    def save_user(self, user: User):
        path = self._get_path_by_user_name(user.name)
        with open(path, "w") as file:
            file.write(json.dumps(user.toJson()))

    def _get_path_by_user_name(self, user_name: str) -> str:
        return os.path.join(self._folder, _format_file_name(user_name))

def _format_file_name(user_name: str) -> str:
    return user_name.replace(" ", "_") + ".json"