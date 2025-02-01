"""
This module handles the conversion of JSON files of characters into Character
objects in the program
"""

from maelstrom.dataClasses.activeAbilities import AbstractActive, createDefaultActives, getActiveAbilityList
from maelstrom.dataClasses.character import Character
from maelstrom.loaders.templateloader import MakeCharacterTemplateRepository

NAME_TO_ACTIVE = dict()
for active in getActiveAbilityList():
    NAME_TO_ACTIVE[active.name] = active

class EnemyLoader:
    """
    loads enemies based upon templates
    """
    
    def __init__(self):
        self._template_repository = MakeCharacterTemplateRepository()

    def load(self, name: str) -> Character:
        """
        constructs a character with the given name, if a template for such a 
        character exists in the repository
        """
        template = self._template_repository.get(name)
        if template is None:
            raise ValueError(f'invalid character name: {name}')
        constructed = Character(
            name = template.name,
            element = template.element,
            stats = {
                'control': template.control,
                'resistance': template.resistance,
                'energy': template.energy,
                'potency': template.potency,
                'luck': template.luck
            },
            actives = createDefaultActives(template.element)
        )
        return constructed        

    def get_options(self) -> list[str]:
        return [option.name for option in self._template_repository.get_all()]

def load_character(as_json: dict) -> Character:
    as_json = as_json.copy()
    as_json["actives"] = [_load_active(data) for data in as_json["actives"]]
    return Character(**as_json)

def _load_active(name: str) -> AbstractActive:
    if name not in NAME_TO_ACTIVE:
        raise Exception(f'no active defined with name "{name}"')
    return NAME_TO_ACTIVE[name]
