from maelstrom.util.stringUtil import entab

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