"""
This module handles the conversion of JSON files of characters into Character
objects in the program
"""



from maelstrom.dataClasses.activeAbilities import createDefaultActives, getActiveAbilityList
from maelstrom.dataClasses.character import Character
from maelstrom.dataClasses.item import getItemList
from maelstrom.dataClasses.passiveAbilities import getPassiveAbilityList
from maelstrom.dataClasses.team import Team
from maelstrom.loaders.templateloader import MakeCharacterTemplateRepository




NAME_TO_ACTIVE = dict()
for active in getActiveAbilityList():
    NAME_TO_ACTIVE[active.name] = active

NAME_TO_ITEM = dict()
for item in getItemList():
    NAME_TO_ITEM[item.name] = item

NAME_TO_PASSIVE = dict()
for passive in getPassiveAbilityList():
    NAME_TO_PASSIVE[passive.name] = passive



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
            actives = createDefaultActives(template.element),
            passives = getPassiveAbilityList()
        )
        return constructed        

    def getOptions(self) -> 'list[str]':
        return [option.name for option in self._template_repository.get_all()]



"""
These types of objects are not stored in a directory, so don't subclass
AbstractJsonLoader for them.
"""

def loadTeam(asJson: dict)->"Team":
    asJson["members"] = [loadCharacter(member) for member in asJson["members"]]
    return Team(**asJson)

def loadCharacter(asJson: dict)->"Character":
    asJson = asJson.copy()
    asJson["actives"] = [loadActive(data) for data in asJson["actives"]]
    asJson["passives"]= [loadPassive(name) for name in asJson["passives"]]
    asJson["equippedItems"] = [loadItem(data) for data in asJson["equippedItems"]]
    return Character(**asJson)

def loadActive(name: str) -> 'AbstractActive':
    if name not in NAME_TO_ACTIVE:
        raise Exception(f'no active defined with name "{name}"')
    return NAME_TO_ACTIVE[name]

def loadPassive(name: str)->"AbstractPassive":
    if name not in NAME_TO_PASSIVE:
        raise Exception(f'no passives defined with name "{name}"')
    return NAME_TO_PASSIVE[name]

def loadItem(name: str)->"Item":
    if name not in NAME_TO_ITEM:
        raise Exception(f'no item defined with name "{name}"')
    return NAME_TO_ITEM[name]
