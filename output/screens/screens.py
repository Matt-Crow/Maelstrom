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

        lines = msg.split("\n")

        for line in lines:
            endOfWord = line.find(' ', SCREEN_COLS - x - 1)
            if endOfWord == -1:
                endOfWord = len(line)
            while endOfWord != -1: # too wide to fit on one row
                # write across multiple rows
                self.addLine(x, y, line[:endOfWord])
                y = y + 1
                line = line[endOfWord + 1:]
                endOfWord = line.find(' ', SCREEN_COLS - x - 1)
            # by now, the line is narrow enough to fit
            if len(line) != 0:
                self.addLine(x, y, line)
                y = y + 1

    def addLine(self, x, y, msg):
        print(msg)
        msg = str(msg)
        length = len(msg)
        numChars = length if length + x - 1 < SCREEN_COLS else SCREEN_COLS - x - 1
        for i in range(numChars):
            if msg[i] == '\n':
                y = y + 1
            else:
                self.content[y][x + i] = msg[i]

    def display(self):
        for row in self.content:
            for cell in row:
                print(cell, sep='', end='')
            print()
