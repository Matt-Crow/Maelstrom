"""
This module is responsible for loading character templates from a file.
"""

import csv
from maelstrom.characters.template import CharacterTemplate

class CharacterTemplateLoader:
    """
    Loads character templates from a file.
    """

    def __init__(self, templates: list[CharacterTemplate]=[]):
        """
        Pre-loads this with the given templates
        """
        self._cache = dict()
        for template in templates:
            self.add_character_template(template)
    
    def add_character_template(self, template: CharacterTemplate):
        self._cache[template.name.lower()] = template
    
    def load_character_template_file(self, type: str):
        """
        Loads all character templates from a file
        """
        # TODO another file for active & passive pools
        with open("data/character-templates.csv", mode='r') as file:
            # skipinitialspace ignores spaces before headers
            reader = csv.DictReader(file, skipinitialspace=True) 
            for row in reader:
                character = self._row_to_character(row)
                if character.type == type:
                    self.add_character_template(character)
    
    def _row_to_character(self, row: dict[str, str]) -> CharacterTemplate:
        return CharacterTemplate(
            name=row['name'].strip(),
            element=row['element'].lower(),
            type=row['type'].strip(),
            control=int(row['control']),
            resistance=int(row['resistance']),
            potency=int(row['potency']),
            luck=int(row['luck']),
            energy=int(row['energy'])
        )

    def get_character_template_by_name(self, name: str) -> CharacterTemplate|None:
        return self._cache.get(name.lower())
    
    def get_all_character_templates(self) -> list[CharacterTemplate]:
        return list(self._cache.values())


def make_starter_template_loader() -> CharacterTemplateLoader:
    """Returns a loader which provides starter templates"""
    starter_loader = CharacterTemplateLoader()
    starter_loader.load_character_template_file("starter")
    return starter_loader

def make_enemy_template_loader() -> CharacterTemplateLoader:
    """Returns a loader which provides enemy templates"""
    enemy_loader = CharacterTemplateLoader()
    enemy_loader.load_character_template_file("enemy")
    return enemy_loader

def make_recruit_template_loader() -> CharacterTemplateLoader:
    """Returns a loader which provides recruit templates"""
    recruit_loader = CharacterTemplateLoader()
    recruit_loader.load_character_template_file("recruit")
    return recruit_loader
