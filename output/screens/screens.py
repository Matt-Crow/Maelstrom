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
        length = len(msg)
        numChars = length if length + x < SCREEN_COLS else SCREEN_COLS - x
        for i in range(numChars):
            self.content[y][x + i] = msg[i]

    def display(self):
        for row in self.content:
            for cell in row:
                print(cell, sep='', end='')
            print()
