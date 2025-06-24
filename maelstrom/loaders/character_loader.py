from maelstrom.characters.specification import CharacterSpecification
from maelstrom.dataClasses.activeAbilities import createDefaultActives
from maelstrom.dataClasses.character import Character
from maelstrom.loaders.character_template_loader import make_enemy_template_loader


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

