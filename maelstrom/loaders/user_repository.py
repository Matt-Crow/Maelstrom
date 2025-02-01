"""
This module is responsible for loading and storing users.
"""

import json
from os import walk
import os
from maelstrom.characters.specification import json_dict_to_character_specification
from maelstrom.dataClasses.team import Team
from maelstrom.util.user import User
from maelstrom.loaders.character_loader import load_character

class UserRepository:
    """
    Loads and stores users.
    """

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
            specs = [json_dict_to_character_specification(e) for e in as_json["specificationTest"]]
            #for spec in specs:
            #    print(spec)
            #    input()

            team = Team(
                as_json["name"], 
                [load_character(member) for member in as_json["partyDetails"]]
            )

            return User(
                name = as_json["name"],
                team = team,
                inventory = []
            )
    
    def save_user(self, user: User):
        path = self._get_path_by_user_name(user.name)
        j = user.toJson()
        j["specificationTest"] = [c.to_specification().to_dict() for c in user.team.members]
        j["partyDetails"] = [m.toJson() for m in user.team.members]

        # try to convert before writing to file to avoid truncating file if json.dumps fails
        as_str = json.dumps(j)
        with open(path, "w") as file:
            file.write(as_str)

    def _get_path_by_user_name(self, user_name: str) -> str:
        file_name = user_name.replace(" ", "_") + ".json"
        return os.path.join(self._folder, file_name)
