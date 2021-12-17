


from util.serialize import JsonSerializer
from characters.character import PlayerCharacter, EnemyCharacter
from characters.item import Item
from characters.passives import Threshhold, OnHitGiven, OnHitTaken
from characters.actives.actives import AbstractActive
from characters.stat_classes import Stat



class StatSerializer(JsonSerializer):
    def __init__(self):
        super().__init__("stat")

    def toJsonDict(self, obj):
        return obj.base

class AbstractCustomizableSerializer(JsonSerializer):
    def __init__(self, type, otherAttrs = [], otherHelpers = dict()):
        super().__init__(type, [
            "name",
            "customizationPoints",
            "stats"
        ], {
            Stat.__name__: StatSerializer()
        })
        for attr in otherAttrs:
            self.serializedAttributes.append(attr)
        self.helpers = dict(**otherHelpers, **self.helpers) # check syntax

class AbstractActiveSerializer(AbstractCustomizableSerializer):
    def __init__(self, type):
        super().__init__(type, [
            "cost"
        ])

class AbstractPassiveSerializer(AbstractCustomizableSerializer):
    def __init__(self, type):
        super().__init__(type, [
            "boostedStat",
            "targetsUser"
        ])

class ThreshholdSerializer(AbstractPassiveSerializer):
    def __init__(self):
        super().__init__("Threshhold Passive")

class OnHitGivenSerializer(AbstractPassiveSerializer):
    def __init__(self):
        super().__init__("On Hit Given Passive")

class OnHitTakenSerializer(AbstractPassiveSerializer):
    def __init__(self):
        super().__init__("On Hit Taken Passive")

class ItemSerializer(AbstractCustomizableSerializer):
    def __init__(self):
        super().__init__("Item", [
            "itemType",
            "desc",
            "boostedStat"
        ])

class AbstractCharacterSerializer(AbstractCustomizableSerializer):
    def __init__(self, type):
        super().__init__(
            type,
            [
                "element",
                "xp",
                "level",
                "actives",
                "passives",
                "equippedItems"
            ], {
                AbstractActive.__name__: AbstractActiveSerializer("AbstractActive"),
                MeleeAttack.__name__: AbstractActiveSerializer("MeleeAttack"),
                Threshhold.__name__: ThreshholdSerializer(),
                OnHitGiven.__name__: OnHitGivenSerializer(),
                OnHitTaken.__name__: OnHitTakenSerializer(),
                Item.__name__: ItemSerializer()
            }
        )

class PlayerCharacterSerializer(AbstractCharacterSerializer):
    def __init__(self):
        super().__init__("PlayerCharacter")

class EnemyCharacterSerializer(AbstractCharacterSerializer):
    def __init__(self):
        super().__init__("EnemyCharacter")


"""
Team serializers
"""

class AbstractTeamSerializer(JsonSerializer):
    def __init__(self, type: str):
        super().__init__(type, ["name", "members"], {
            PlayerCharacter.__name__: PlayerCharacterSerializer,
            EnemyCharacter.__name__: EnemyCharacterSerializer
        })

class PlayerTeamSerializer(AbstractTeamSerializer):
    def __init__(self):
        super().__init__("PlayerTeam")
        self.serializedAttributes.append("inventory")
        self.helpers[Item.__name__] = ItemSerializer()

class EnemyTeamSerializer(AbstractTeamSerializer):
    def __init__(self):
        super().__init__("EnemyTeam")
