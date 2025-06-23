"""
This module handles the conversion of JSON files of characters into Character
objects in the program
"""

from maelstrom.characters.specification import CharacterSpecification
from maelstrom.dataClasses.activeAbilities import AbstractActive, createDefaultActives, get_all_actives
from maelstrom.dataClasses.character import Character
from maelstrom.loaders.character_template_loader import make_enemy_template_loader

NAME_TO_ACTIVE = dict()
for active in get_all_actives():
    NAME_TO_ACTIVE[active.name] = active

class EnemyLoader:
    """
    loads enemies based upon templates
    """
    
    def __init__(self):
        self._templates = make_enemy_template_loader()

    def load(self, name: str) -> Character:
        """
        constructs a character with the given name, if a template for such a 
        character exists in the repository
        """
        template = self._templates.get_character_template_by_name(name)
        constructed = Character(
            template=template,
            specification=CharacterSpecification(name=name),
            actives=createDefaultActives(template.element)
        )
        return constructed        

    def get_options(self) -> list[str]:
        return [option.name for option in self._templates.get_all_character_templates()]

def load_active(name: str) -> AbstractActive:
    if name not in NAME_TO_ACTIVE:
        raise Exception(f'no active defined with name "{name}"')
    return NAME_TO_ACTIVE[name]
