"""
Handles loading the contents of data/character-templates.csv
"""

from abc import ABC, abstractmethod
from collections import OrderedDict
import csv
from maelstrom.characters.template import CharacterTemplate


class CharacterTemplateLoader(ABC):
    """
    loads character templates from an external resource
    """

    @abstractmethod
    def get(self, name: str) -> CharacterTemplate:
        """
        returns the template of a character with the given name, or None if no
        such character template exists
        """
        pass

    @abstractmethod
    def get_all(self) -> 'list[CharacterTemplate]':
        """
        returns all available character templates
        """
        pass


class InMemoryCharacterTemplateLoader(CharacterTemplateLoader):
    """
    stores character templates in memory
    """

    def __init__(self, templates: 'list[CharacterTemplate]'=[]):
        """
        creates a new in memory template loader pre-loaded with the given data
        """
        super().__init__()
        self._cache = dict()
        for template in templates:
            self.add(template)

    def add(self, template: CharacterTemplate):
        """
        adds a character template such that it can be retrieved later
        """
        self._cache[template.name] = template

    def get(self, name: str) -> CharacterTemplate:
        return self._cache.get(name)
    
    def get_all(self) -> 'list[CharacterTemplate]':
        return list(self._cache.values())


class CsvCharacterTemplateLoader(CharacterTemplateLoader):
    def __init__(self):
        self._cache = dict()
        self._loaded = False

    def get(self, name: str) -> CharacterTemplate:
        if not self._loaded:
            self._load_file()
        return self._cache.get(name.lower())

    def get_all(self) -> 'list[CharacterTemplate]':
        if not self._loaded:
            self._load_file()
        return list(self._cache.values())
    
    def _load_file(self):
        # todo another file for active & passive pools
        with open('data/character-templates.csv', mode='r') as file:
            # skipinitialspace ignores spaces before headers
            reader = csv.DictReader(file, skipinitialspace=True) 
            for row in reader:
                self._cache[row['name'].strip().lower()] = self._row_to_character(row)
        self._loaded = True

    def _row_to_character(self, row: 'OrderedDict[str, str]') -> CharacterTemplate:
        return CharacterTemplate(
            name=row['name'].strip(),
            element=row['element'].lower(),
            control=int(row['control']),
            resistance=int(row['resistance']),
            potency=int(row['potency']),
            luck=int(row['luck']),
            energy=int(row['energy'])
        )
    

class CharacterTemplateRepository:
    """
    loads character templates from a backing store
    """
    
    def __init__(self, character_template_loader: CharacterTemplateLoader):
        """
        creates a new character template repository with the given backing store
        """
        self._character_template_loader = character_template_loader

    def get(self, name: str) -> CharacterTemplate:
        """
        retrieves a character template with the given name from the repository, 
        if such a character template exists
        """
        return self._character_template_loader.get(name)
    
    def get_all(self) -> 'list[CharacterTemplate]':
        """
        retrieves all available character templates
        """
        return self._character_template_loader.get_all()
    

def MakeCharacterTemplateRepository() -> CharacterTemplateRepository:
    """
    returns the default character template repository
    """
    return CharacterTemplateRepository(CsvCharacterTemplateLoader())