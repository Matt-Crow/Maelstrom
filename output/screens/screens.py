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

    def add(self, x, y, msg):
        msg = str(msg)
        maxChars = SCREEN_COLS - x
        if maxChars < 0:
            raise RuntimeError("x is too large")

        newline = msg.find('\n', 0, maxChars)
        if newline != -1:
            self.add(x, y + 1, msg[newline + 1:]) # recur with everything after \n
            msg = msg[:newline]
        # by now, msg either fits or did not have a newline
        if len(msg) > maxChars: # doesn't fit on one line
            endOfWord = msg.rfind(' ', 0, maxChars + 1) # end of last word that fits on screen
            if endOfWord == -1: # no words fit on screen
                self.add(x, y + 1, msg[maxChars:]) # recur with everything that won't fit
                msg = msg[:maxChars]
            else:
                self.add(x, y + 1, msg[endOfWord + 1:]) # recur after to that last space
                msg = msg[:endOfWord]

        # Base case: msg fits and has no newlines
        length = len(msg)
        for i in range(length):
            self.content[y][x + i] = msg[i]

    def display(self):
        for row in self.content:
            for cell in row:
                print(cell, sep='', end='')
            print()
