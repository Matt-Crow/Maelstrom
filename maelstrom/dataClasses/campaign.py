"""
this module will eventually include a Campaign class - a collection of Areas
"""



from util.stringUtil import entab
from util.serialize import AbstractJsonSerialable



class Location(AbstractJsonSerialable):
    """
    Locations provide flavor text for an Area
    """

    def __init__(self, **kwargs):
        """
        required kwargs:
        - name: str
        - description: str
        """
        super().__init__(**dict(kwargs, type="Location"))
        self.name = kwargs["name"]
        self.description = kwargs["description"]
        self.addSerializedAttributes("name", "description")

    def __str__(self)->str:
        return f'Location: {self.name}'

    def getDisplayData(self)->str:
        """
        gets data to output
        """
        return f'{self.name}: "{self.description}"'


class Level(AbstractJsonSerialable):
    """
    A level pits two teams against each other in an Encounter
    """

    def __init__(self, **kwargs):
        """
        required kwargs:
        - name: str
        - description: str
        - prescript: str
        - postscript: str
        - enemyNames: List<str>
        - enemyLevel: int
        """
        super().__init__(**dict(kwargs, type="Level"))

        self.name = kwargs["name"]
        self.description = kwargs["description"]
        self.prescript = kwargs["prescript"]
        self.postscript = kwargs["postscript"]
        self.enemyNames = kwargs["enemyNames"]
        self.enemyLevel = kwargs["enemyLevel"]

        self.addSerializedAttributes(
            "name",
            "description",
            "prescript",
            "postscript",
            "enemyNames",
            "enemyLevel"
        )

    def __str__(self)->str:
        return f'Level: {self.name}'

    def getDisplayData(self)->str:
        lines = [
            f'Level: {self.name}',
            entab(f'"{self.description}"')
        ]
        for name in self.enemyNames:
            lines.append(f'* {name} Lv. {self.enemyLevel}')

        return "\n".join(lines)
