"""
This module provides the basic structure of the screens the program displays

Primary exports:

"""

from enum import Enum, auto
import math
import sys
import re
from util.utilities import lengthOfLongest

SCREEN_COLS = 80
SCREEN_ROWS = 40

"""
displayCharacterStats(Character)
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

BORDER = "#"
OPTION_ROWS = 5 # allows for 2 columns of 5 options each

class GameScreenMode(Enum):
    ONE_COL = auto()
    SPLIT = auto()

class GameScreen(Screen):
    def __init__(self):
        super(GameScreen, self).__init__()
        self.setTitle("Maelstrom")
        self.nextBodyLine = 0
        self.nextLeftLine = 0
        self.nextRightLine = 0
        self.options = []
        self.clearOptions()
        self.mode = GameScreenMode.SPLIT

    def setTitle(self, title: str):
        self.outlineBox(0, 0, SCREEN_COLS, 3, BORDER, " ")
        center = int((SCREEN_COLS) / 2) - len(title)
        self.add(center, 1, title)

    def fillBox(self, x, y, w, h, character):
        for i in range(h):
            self.add(x, y + i, character * w)

    def outlineBox(self, x, y, w, h, outlineCharacter, fillCharacter):
        self.fillBox(x, y, w, h, outlineCharacter)
        self.fillBox(x + 1, y + 1, w - 2, h - 2, fillCharacter)

    def clearOptions(self):
        self.options.clear()
        numRows = OPTION_ROWS + 2 # one above, one below the options
        #self.add(0, SCREEN_ROWS - numRows, BORDER * SCREEN_COLS * numRows)
        self.outlineBox(0, SCREEN_ROWS - numRows, SCREEN_COLS, numRows, BORDER, " ")

    def display(self):
        if self.mode == GameScreenMode.ONE_COL:
            self.outlineBox(0, 3, SCREEN_COLS, SCREEN_ROWS - 3 - OPTION_ROWS - 2, BORDER, " ")
        elif self.mode == GameScreenMode.SPLIT:
            self.outlineBox(0, 3, int(SCREEN_COLS / 2), SCREEN_ROWS - 3 - OPTION_ROWS - 2, BORDER, " ")
            self.outlineBox(int(SCREEN_COLS / 2), 3, int(SCREEN_COLS / 2), SCREEN_ROWS - 3 - OPTION_ROWS - 2, BORDER, " ")
        super(GameScreen, self).display()

NUM_BODY_ROWS = 10

class SimplerGameScreen:
    def __init__(self):
        self.title = "Maelstrom"
        self.body = []
        self.leftBody = []
        self.rightBody = []
        self.options = []
        self.mode = GameScreenMode.ONE_COL

    def setTitle(self, title: str):
        self.title = title[:(SCREEN_COLS - 4)] # ensures title fits

    def addBodyRows(self, rows: "List<String>"):
        for row in rows:
            self.addBodyRow(row)

    def addBodyRow(self, row: str):
        row = self.format(row)
        if "\n" in row:
            self.addBodyRows(row.split("\n"))
        elif len(row) > SCREEN_COLS - 4: # make sure it fits
            self.addBodyRows(self.wrap(row))
        else:
            self.body.append(row)

    def format(self, row: str)->str:
        return row.replace("\t", " " * 4)

    def wrap(self, row: str)->"List<str>":
        rows = []
        maxWidth = SCREEN_COLS - 4
        if self.mode == GameScreenMode.SPLIT:
            maxWidth = int(maxWidth / 2)

        while len(row.strip()) is not 0:
            wordBreak = row.rfind(" ", 0, maxWidth)
            firstNonSpace = re.search("[^ ]", row)
            indentation = 0 if not firstNonSpace else firstNonSpace.start()
            if wordBreak < indentation: # no suitable break point
                rows.append(row[:maxWidth])
                row = indentation * " " + row[maxWidth:]
            else:
                rows.append(row[:wordBreak])
                row = indentation * " " + row[(wordBreak + 1):]

        return rows

    """
    There may need to be some limit on the number of options this can be given
    """
    def addOption(self, option: str):
        self.options.append(option)

    def setMode(self, mode):
        self.mode = mode

    def clear(self):
        self.title = "Maelstrom"
        self.clearBody()

    def clearBody(self):
        self.body.clear()
        self.leftBody.clear()
        self.rightBody.clear()

    def clearOptions(self):
        self.options.clear()

    def display(self):
        self.write(sys.stdout)

    def displayAndPause(self):
        self.display()
        input("press enter or return to continue")

    def write(self, out): # can use a file as out
        bodyLines = max(len(self.body), len(self.leftBody), len(self.rightBody))
        currLine = 0
        """
        Displays NUM_BODY_ROWS rows of the body at a time
        """
        while currLine < bodyLines:
            self.writeTitle(out)
            self.writeBody(out, currLine)
            currLine += NUM_BODY_ROWS
            if currLine < bodyLines: # more lines
                self.writeOptions(out, []) # just print empty options box
                input("press enter or return to continue")
        self.writeOptions(out, self.options)
        print("Choose an option:")

    def writeTitle(self, out):
        print(BORDER * SCREEN_COLS, file=out)
        leftPadding = math.floor((SCREEN_COLS - len(self.title)) / 2) - 1
        rightPadding = math.ceil((SCREEN_COLS - len(self.title)) / 2) - 1
        print(f'{BORDER}{leftPadding * " "}{self.title}{rightPadding * " "}{BORDER}')
        print(BORDER * SCREEN_COLS, file=out)

    """
    Writes the body lines withing [firstLineNum, firstLineNum + NUM_BODY_ROWS)
    """
    def writeBody(self, out, firstLineNum=0):
        print(BORDER * SCREEN_COLS, file=out)
        if self.mode == GameScreenMode.ONE_COL:
            self.writeOneCol(out, firstLineNum)
        else:
            raise "not implemented"
        print(BORDER * SCREEN_COLS, file=out)

    def writeOneCol(self, out, firstLineNum=0):
        rowNum = 0
        spaces = 0
        row = None
        while rowNum < NUM_BODY_ROWS:
            if rowNum + firstLineNum < len(self.body):
                row = self.body[rowNum + firstLineNum]
                spaces = SCREEN_COLS - 4 - len(row)
                print(f'{BORDER} {row}{" " * spaces} {BORDER}', file=out)
            else:
                print(f'{BORDER} {" " * (SCREEN_COLS - 4)} {BORDER}')
            rowNum = rowNum + 1

    def writeOptions(self, out, options):
        print(BORDER * SCREEN_COLS, file=out)

        # get column widths
        colWidths = []
        colStart = 0
        while colStart < len(options): #                                                 + 1 so there's a space between columns
            colWidths.append(lengthOfLongest(options[colStart:(colStart + OPTION_ROWS)]) + 1)
            colStart += OPTION_ROWS # next column
        """
        colWidths[0] contains the width of the first OPTION_ROWS options,
        colWidths[1] contains the width of the next OPTION_ROWS options,
        etc
        """

        # setup
        numCols = len(colWidths)
        msg = ""
        i = 0
        for rowNum in range(OPTION_ROWS):
            msg = ""
            for colNum in range(numCols):
                i = rowNum + colNum * OPTION_ROWS
                if i < len(options):
                    if colNum is not 0:
                        msg += f'{BORDER} ' # separate columns with border
                    msg += f'{(i + 1):2}: {options[i].ljust(colWidths[colNum])}'
            msg = msg.ljust(SCREEN_COLS - 4)[:(SCREEN_COLS - 4)] # justify and trim it to fit exactly
            print(f'{BORDER} {msg} {BORDER}', file=out)

        print(BORDER * SCREEN_COLS, file=out)

def displayCharacterStats(character):
    screen = SimplerGameScreen()
    screen.setTitle(f'{character.name} Lv. {character.level}')
    displayData = character.getDisplayData()
    screen.addBodyRows(displayData)
    screen.display()
