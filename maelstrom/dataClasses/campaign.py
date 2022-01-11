"""
this module will eventually include a Campaign class - a collection of Areas
"""



from maelstrom.util.stringUtil import entab
from maelstrom.util.serialize import AbstractJsonSerialable



class Area(AbstractJsonSerialable):
    """
    a collection of Levels and Locations
    """

    def __init__(self, **kwargs):
        """
        required kwargs:
        - name: str
        - description: str
        - locations: List<Location>. Defaults to []
        - levels: List<Level>. Defaults to []
        """
        super().__init__(**dict(kwargs, type="Area"))
        self.name = kwargs["name"]
        self.description = kwargs["description"]
        self.locations = kwargs.get("locations", [])
        self.levels = kwargs.get("levels", [])
        self.addSerializedAttributes("name", "description", "locations", "levels")

    def __str__(self)->str:
        return f'Area: {self.name}'

    def getDisplayData(self)->str:
        lines = [
            f'Area: {self.name}',
            entab(self.description)
        ]

        if len(self.locations) > 0:
            lines.append("Locations:")
            for location in self.locations:
                lines.append(entab(location.getDisplayData()))

        if len(self.levels) > 0:
            lines.append("Levels:")
            for level in self.levels:
                lines.append(entab(level.getDisplayData()))

        return "\n".join(lines)



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
            lines.append(entab(f'* {name} Lv. {self.enemyLevel}'))

        return "\n".join(lines)
