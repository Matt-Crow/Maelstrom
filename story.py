from utilities import *

class Story:
    def __init__(self, story):
        self.story = to_list(story)

    def print_story(self):
        for script in self.story:
            Op.add(script)
            Op.dp()
            pause()
