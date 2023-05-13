import unittest
from maelstrom.characters.template import CharacterTemplate
from maelstrom.loaders.templateloader import CharacterTemplateRepository, CsvCharacterTemplateLoader, InMemoryCharacterTemplateLoader

class TestLoaders(unittest.TestCase):
    def test_characters(self):
        sut = CsvCharacterTemplateLoader()
        actual = sut.get_all()
        self.assertNotEqual(0, len(actual))

    def test_CharacterTemplateRepository(self):
        loader = InMemoryCharacterTemplateLoader()
        loader.add(CharacterTemplate('bar', 'wind'))
        sut = CharacterTemplateRepository(loader)
        no_exist = sut.get('foo')
        exists = sut.get('bar')
        self.assertTrue(no_exist is None)
        self.assertFalse(exists is None)