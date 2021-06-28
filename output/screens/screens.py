"""
This module provides the basic structure of the screens the program displays
"""

SCREEN_COLS = 80
SCREEN_ROWS = 40

"""

"""
class Screen:
    def __init__(self):
        self.content = []
        row = []
        for colNum in range(SCREEN_COLS):
            row.append('*')
        for rowNum in range(SCREEN_ROWS):
            self.content.append(row.copy())

    def clear(self):
        for rowNum in range(SCREEN_ROWS):
            for colNum in range(SCREEN_COLS):
                self.content[rowNum][colNum] = ' '

    def add(self, x, y, msg)->int: # returns number of rows added
        msg = str(msg)
        maxChars = SCREEN_COLS - x
        if maxChars < 0:
            raise RuntimeError("x is too large")

        rows = 0
        newline = msg.find('\n', 0, maxChars)
        if newline != -1:
            rows = self.add(x, y + 1, msg[newline + 1:]) # recur with everything after \n
            msg = msg[:newline]
        # by now, msg either fits or did not have a newline
        if len(msg) > maxChars: # doesn't fit on one line
            endOfWord = msg.rfind(' ', 0, maxChars + 1) # end of last word that fits on screen
            if endOfWord == -1: # no words fit on screen
                rows = self.add(x, y + 1, msg[maxChars:]) # recur with everything that won't fit
                msg = msg[:maxChars]
            else:
                rows = self.add(x, y + 1, msg[endOfWord + 1:]) # recur after to that last space
                msg = msg[:endOfWord]

        # Base case: msg fits and has no newlines
        length = len(msg)
        for i in range(length):
            self.content[y][x + i] = msg[i]
        rows = rows + 1

        return rows

    def display(self):
        for row in self.content:
            for cell in row:
                print(cell, sep='', end='')
            print()

class AreaScreen(Screen):
    def __init__(self, area):
        super(AreaScreen, self).__init__()
        self.setTitle(area.name)
        endOfDesc = self.setDescription(area.desc)
        self.listLocations(area.locations, endOfDesc + 1)
        self.listLevels(area.levels)

    def setTitle(self, title: str):
        self.add(0, 0, "~" * SCREEN_COLS * 3) # 3 rows of "~"
        center = int((SCREEN_COLS) / 2) - len(title)
        self.add(center, 1, title)

    def setDescription(self, description: str):
        rows = self.add(4, 3, description)
        return rows + self.add(0, 3 + rows, "\n" + "~" * SCREEN_COLS)

    def listLocations(self, locations: "list<Location>", y: int):
        self.add(4, y, "Locations:")
        for i in range(len(locations)):
            self.add(8, y + i + 1, f'* {locations[i].name}')

    def listLevels(self, levels: "list<Level>"):
        y = SCREEN_ROWS - len(levels) - 1 # todo: add room for options
        self.add(4, y, "Levels:")
        for i in range(len(levels)):
            self.add(8, y + i + 1, f'* {levels[i].name}')
