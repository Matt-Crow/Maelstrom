"""
This module is responsible for loading and storing users.
"""

import json
from os import walk
import os
from maelstrom.characters.specification import json_dict_to_character_specification
from maelstrom.dataClasses.activeAbilities import AbstractActive, get_all_actives
from maelstrom.dataClasses.character import Character
from maelstrom.dataClasses.team import User
from maelstrom.loaders.character_template_loader import make_player_character_template_loader


class UserRepository:
    """
    Loads and stores users.
    """

    def __init__(self):
        self._folder = os.path.abspath("users")
        self._character_templates = make_player_character_template_loader()

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
            specs = [json_dict_to_character_specification(e) for e in as_json["party"]]
            party = []
            for spec in specs:
                template = self._character_templates.get_character_template_by_name(spec.name)
                character = Character(
                    template=template,
                    specification=spec,
                    actives = [load_active(active_name) for active_name in spec.active_names]
                )
                party.append(character)

            return User(as_json["name"], party)
    
    def save_user(self, user: User):
        path = self._get_path_by_user_name(user.name)
        as_dict = dict(
            name=user.name,
            party=[c.to_specification().to_dict() for c in user.party]
        )

        # try to convert before writing to file to avoid truncating file if json.dumps fails
        as_str = json.dumps(as_dict)
        with open(path, "w") as file:
            file.write(as_str)

    def _get_path_by_user_name(self, user_name: str) -> str:
        file_name = user_name.replace(" ", "_") + ".json"
        return os.path.join(self._folder, file_name)


NAME_TO_ACTIVE = dict()
for active in get_all_actives():
    NAME_TO_ACTIVE[active.name] = active

def load_active(name: str) -> AbstractActive:
    if name not in NAME_TO_ACTIVE:
        raise Exception(f'no active defined with name "{name}"')
    return NAME_TO_ACTIVE[name]