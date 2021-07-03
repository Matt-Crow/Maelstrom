"""
This module provides the basic structure of the screens the program displays

Primary exports:
* displayCharacterStats(Character)
* displayTeamUndetailed(Team)
"""

from enum import Enum, auto
import math
import sys
import re
from util.stringUtil import lengthOfLongest



def displayCharacterStats(character):
    screen = SimplerGameScreen()
    screen.setTitle(f'{character.name} Lv. {character.level}')
    displayData = character.getDisplayData()
    screen.addBodyRows(displayData.split("\n"))
    screen.display()

def displayTeamUndetailed(team):
    screen = SimplerGameScreen()
    screen.setTitle(f'Team: {team.name}')
    displayData = team.getShortDisplayData()
    screen.addBodyRow(displayData)
    screen.display()



SCREEN_COLS = 80
SCREEN_ROWS = 40

BORDER = "#"
OPTION_ROWS = 5

NUM_BODY_ROWS = 10

class RowStyle:
    def wrap(self, msg: str)->"list<str>":
        pass

    def format(self, msg: str)->"list<str>":
        pass

class BorderedRow:
    def __init__(self, rowWidth=SCREEN_COLS, border="#", padding=" "):
        super().__init__()
        self.border = border
        self.padding = padding
        self.bodyWidth = rowWidth - (len(border) + len(padding)) * 2

    def wrap(self, msg: str)->"list<str>":
        rows = []

        while len(msg.strip()) is not 0:
            wordBreak = msg.rfind(" ", 0, self.bodyWidth)
            firstNonSpace = re.search("[^ ]", msg)
            indentation = 0 if not firstNonSpace else firstNonSpace.start()
            if wordBreak < indentation: # no suitable break point
                rows.append(msg[:maxWidth])
                msg = indentation * " " + msg[self.bodyWidth:]
            else:
                rows.append(msg[:wordBreak])
                msg = indentation * " " + msg[(wordBreak + 1):]

        return rows

    def format(self, msg: str)->"list<str>":
        rows = []

        if "\n" in msg:
            for line in msg.split("\n"):
                rows.extend(self.format(line))
        elif len(msg) > self.bodyWidth:
            rows.extend(self.wrap(msg))
        else:
            rows.append(msg)

        return [f'{self.border}{self.padding}{row.ljust(self.bodyWidth, self.padding)}{self.padding}{self.border}' for row in rows]



class SimplerGameScreen:
    def __init__(self):
        self.title = "Maelstrom"
        self.body = [] # List of BodyRows
        self.options = []

    def setTitle(self, title: str):
        self.title = title[:(SCREEN_COLS - 4)] # ensures title fits

    def addBodyRows(self, rows: "List<String>"):
        for row in rows:
            self.addBodyRow(row)

    def addBodyRow(self, row: str):
        row = self.format(row)
        self.body.extend(BorderedRow().format(row))

    def addSplitRow(self, left: str, right: str):
        left = self.format(left)
        right = self.format(right)

        # deal with newlines
        if "\n" in left:
            leftLines = left.split("\n")
        else:
            leftLines = [left]

        if "\n" in right:
            rightLines = right.split("\n")
        else:
            rightLines = [right]

        half = int((SCREEN_COLS - 4) / 2) - 2
        leftRows = []
        rightRows = []

        for line in leftLines:
            if len(line) > half:
                leftRows.extend(self.wrap(line, half))
            else:
                leftRows.append(line)

        for line in rightLines:
            if len(line) > half:
                rightRows.extend(self.wrap(line, half))
            else:
                rightRows.append(line)

        # Pair up left and right rows. Rows with no match get paired with spaces
        totalLines = max(len(leftRows), len(rightRows))
        for i in range(totalLines):
            l = ""
            r = ""
            if len(leftRows) > i:
                l = leftRows[i]
            if len(rightRows) > i:
                r = rightRows[i]
            self.body.append(SplitRow(l, r))

    def format(self, row: str)->str:
        return row.replace("\t", " " * 4)

    def wrap(self, row: str, maxWidth: int)->"List<str>":
        rows = []

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

    def clear(self):
        self.title = "Maelstrom"
        self.clearBody()

    def clearBody(self):
        self.body.clear()

    def clearOptions(self):
        self.options.clear()

    def display(self):
        self.write(sys.stdout)

    def displayAndPause(self):
        self.display()
        input("press enter or return to continue")

    def write(self, out): # can use a file as out
        bodyLines = len(self.body)
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
        print(CenterAlignedRow(self.title), file=out)
        print(BORDER * SCREEN_COLS, file=out)

    """
    Writes the body lines withing [firstLineNum, firstLineNum + NUM_BODY_ROWS)
    """
    def writeBody(self, out, firstLineNum=0):
        print(BORDER * SCREEN_COLS, file=out)
        self.writeOneCol(out, firstLineNum)
        print(BORDER * SCREEN_COLS, file=out)

    def writeOneCol(self, out, firstLineNum=0):
        rowNum = 0
        row = None
        while rowNum < NUM_BODY_ROWS:
            if rowNum + firstLineNum < len(self.body):
                row = self.body[rowNum + firstLineNum]
                print(row, file=out)
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


class BodyRowStyle(Enum):
    LEFT_ALIGN = auto()
    RIGHT_ALIGN = auto()
    CENTER_ALIGN = auto()
    SPLIT = auto()

class BodyRow:
    def __init__(self, content: str):
        self.content = content

class LeftAlignedRow(BodyRow):
    def __init__(self, content: str):
        super().__init__(content)

    def __str__(self)->str:
        return f'{BORDER} {self.content.ljust(SCREEN_COLS - 4)} {BORDER}'

class RightAlignedRow(BodyRow):
    def __init__(self, content: str):
        super().__init__(content)

    def __str__(self)->str:
        return f'{BORDER} {self.content.rjust(SCREEN_COLS - 4)} {BORDER}'

class CenterAlignedRow(BodyRow):
    def __init__(self, content: str):
        super().__init__(content)
        maxWidth = SCREEN_COLS - 4
        """
        when maxWidth == len(content), cannot offset
        when len(content) == 1, offset is halfway across the screen
        """
        offset = int((maxWidth - len(content)) / 2)
        self.spacing = " " * offset

    def __str__(self)->str:
        return f'{BORDER} {(self.spacing + self.content).ljust(SCREEN_COLS - 4)} {BORDER}'

class SplitRow(BodyRow):
    def __init__(self, left=None, right=None):
        super().__init__("")

        half = int((SCREEN_COLS - 4) / 2)

        if left is None:
            left = " " * half
        self.left = left

        if right is None:
            right = " " * half
        self.right = right

    def setLeft(self, left: str):
        self.left = left

    def setRight(self, right: str):
        self.right = right

    def __str__(self)->str:
        leftHalf = math.floor((SCREEN_COLS - 4) / 2) - 2
        rightHalf = math.ceil((SCREEN_COLS - 4) / 2) - 2
        return f'{BORDER} {self.left.ljust(leftHalf)} {BORDER}{BORDER} {self.right.ljust(rightHalf)} {BORDER}'



"""
Old stuff down here
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

class GameScreen(Screen):
    def __init__(self):
        super(GameScreen, self).__init__()
        self.setTitle("Maelstrom")
        self.nextBodyLine = 0
        self.nextLeftLine = 0
        self.nextRightLine = 0
        self.options = []
        self.clearOptions()

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
        self.outlineBox(0, 3, int(SCREEN_COLS / 2), SCREEN_ROWS - 3 - OPTION_ROWS - 2, BORDER, " ")
        self.outlineBox(int(SCREEN_COLS / 2), 3, int(SCREEN_COLS / 2), SCREEN_ROWS - 3 - OPTION_ROWS - 2, BORDER, " ")
        super(GameScreen, self).display()
