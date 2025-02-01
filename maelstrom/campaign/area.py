from maelstrom.util.stringUtil import entab

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