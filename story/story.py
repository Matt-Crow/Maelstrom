from utilities import to_list
from output import Op

class Story:
    """
    Used to store strings for story text,
    providing atmosphere
    """
    def __init__(self, story):
        """
        Story is an array of strings, or just a string
        """
        self.story = to_list(story)

    def print_story(self):
        """
        Pauses for dramatic effect
        """
        for script in self.story:
            Op.add(script)
            Op.display()
