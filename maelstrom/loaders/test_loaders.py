import unittest
from maelstrom.characters.template import CharacterTemplate
from maelstrom.loaders.character_template_loader import CharacterTemplateLoader, make_enemy_template_loader

class TestLoaders(unittest.TestCase):
    def test_CharacterTemplateLoader(self):
        sut = CharacterTemplateLoader()
        sut.add_character_template(CharacterTemplate('bar', 'wind'))
        no_exist = sut.get_character_template_by_name('foo')
        exists = sut.get_character_template_by_name('bar')
        self.assertTrue(no_exist is None)
        self.assertFalse(exists is None)

    def test_loading(self):
        sut = make_enemy_template_loader()
        actual = sut.get_all_character_templates()
        self.assertNotEqual(0, len(actual))