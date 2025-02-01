"""
This module is responsible for loading character templates from a file.
"""

from collections import OrderedDict
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
    
    def load_character_template_file(self, path: str):
        """
        Loads all character templates from a file
        """
        # todo another file for active & passive pools
        with open(path, mode='r') as file:
            # skipinitialspace ignores spaces before headers
            reader = csv.DictReader(file, skipinitialspace=True) 
            for row in reader:
                self.add_character_template(self._row_to_character(row))
    
    def _row_to_character(self, row: OrderedDict[str, str]) -> CharacterTemplate:
        return CharacterTemplate(
            name=row['name'].strip(),
            element=row['element'].lower(),
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
