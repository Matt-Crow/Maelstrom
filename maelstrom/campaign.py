"""
A campaign is a collection of story elements and challenges the player can
overcome.

Each player will keep track of the campaign they are playing and their various
statistics within that campaign, such as which levels they have won or lost.
"""

from maelstrom.string_utils import entab

class Level:
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
        - enemy_names: List<str>
        - enemy_level: int
        """
        self.name = kwargs["name"]
        self.description = kwargs["description"]
        self.prescript = kwargs["prescript"]
        self.postscript = kwargs["postscript"]
        self.enemy_names = kwargs["enemy_names"]
        self.enemy_level = kwargs["enemy_level"]

    def __str__(self)->str:
        return f'Level: {self.name}'

    def getDisplayData(self)->str:
        lines = [
            f'Level: {self.name}',
            entab(f'"{self.description}"')
        ]
        for name in self.enemy_names:
            lines.append(entab(f'* {name} Lv. {self.enemy_level}'))

        return "\n".join(lines)
    

class Area:
    """
    a collection of Levels
    """

    def __init__(self, **kwargs):
        """
        required kwargs:
        - name: str
        - description: str
        - levels: List[Level]. Defaults to []
        """
        self.name = kwargs["name"]
        self.description = kwargs["description"]
        self.levels = kwargs.get("levels", [])
        
    def __str__(self)->str:
        return f'Area: {self.name}'

    def getDisplayData(self)->str:
        lines = [
            f'Area: {self.name}',
            entab(self.description)
        ]

        if len(self.levels) > 0:
            lines.append("Levels:")
            for level in self.levels:
                lines.append(entab(level.getDisplayData()))

        return "\n".join(lines)


class Campaign:
    def __init__(self, **kwargs):
        """
        Required kwargs:
        - name: str
        - areas: list[Area]
        """
        self.name = kwargs["name"]
        self.areas = kwargs.get("areas", [])

    def get_area(self, num: int) -> Area:
        return self.areas[num]