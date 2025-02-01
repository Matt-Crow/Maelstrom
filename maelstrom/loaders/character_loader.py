"""
This module handles the conversion of JSON files of characters into Character
objects in the program
"""

from maelstrom.dataClasses.activeAbilities import AbstractActive, createDefaultActives, getActiveAbilityList
from maelstrom.dataClasses.character import Character
from maelstrom.loaders.character_template_loader import CharacterTemplateLoader

NAME_TO_ACTIVE = dict()
for active in getActiveAbilityList():
    NAME_TO_ACTIVE[active.name] = active

class EnemyLoader:
    """
    loads enemies based upon templates
    """
    
    def __init__(self):
        self._templates = CharacterTemplateLoader()
        self._templates.load_character_template_file("data/character-templates/enemies.csv")

    def load(self, name: str) -> Character:
        """
        constructs a character with the given name, if a template for such a 
        character exists in the repository
        """
        template = self._templates.get_character_template_by_name(name)
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
        return [option.name for option in self._templates.get_all_character_templates()]

def load_active(name: str) -> AbstractActive:
    if name not in NAME_TO_ACTIVE:
        raise Exception(f'no active defined with name "{name}"')
    return NAME_TO_ACTIVE[name]
