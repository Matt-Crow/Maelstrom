"""
This module provides the basic structure of the screens the program displays

Primary export:

* Class Screen
    - setTitle(str)
    - addBodyRows(List<str>)
    - addBodyRow(str) # automatically splits newlines into new rows
    - addSplitRow(left: str, right: str)
    - addOption()
    - display()
    - displayAndChoose(prompt)
"""

from enum import Enum, auto
import math
import sys
import re
import subprocess
from inputOutput.input import choose
from inputOutput.output import output, error, CLS_BEFORE_DISPLAY
from util.stringUtil import lengthOfLongest

SCREEN_COLS = 80

BORDER = "#"
OPTION_ROWS = 5

NUM_BODY_ROWS = 10



class Screen:
    def __init__(self):
        self.title = "Maelstrom"
        self.body = [] # List of str
        self.options = []

    def setTitle(self, title: str):
        self.title = title[:(SCREEN_COLS - 4)] # ensures title fits

    def addBodyRows(self, rows: "List<String>"):
        for row in rows:
            self.addBodyRow(row)

    def addBodyRow(self, row: str):
        if type(row) == type("Hello world!"):
            self.body.extend(BorderedRowStyle().format(row))
        else: # check if iterable AFTER checking if string
            try: # https://stackoverflow.com/questions/1952464/in-python-how-do-i-determine-if-an-object-is-iterable
                for item in iter(row):
                    self.body.extend(BorderedRowStyle().format(item))
            except TypeError as neitherIterNorStr:
                self.body.extend(BorderedRowStyle().format(str(row)))

    def addSplitRow(self, left: str, right: str):
        self.body.extend(SplitRowStyle().format(left, right))

    """
    There may need to be some limit on the number of options this can be given
    """
    def addOption(self, option: "any"):
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

    def write(self, out): # can use a file as out
        bodyLines = len(self.body)
        currLine = 0

        """
        Displays NUM_BODY_ROWS rows of the body at a time
        """
        if bodyLines == 0:
            if CLS_BEFORE_DISPLAY:
                try:
                    works = subprocess.call("cls", shell=True)
                    if works != 0: #is false, didn't run
                        works = subprocess.call("clear", shell=True)
                except:
                    error("couldn't clear screen in Screen::display")
            self.writeTitle(out)
            self.writeBody(out, 0) # print blank body

        while currLine < bodyLines:
            if CLS_BEFORE_DISPLAY:
                try:
                    works = subprocess.call("cls", shell=True)
                    if works != 0: #is false, didn't run
                        works = subprocess.call("clear", shell=True)
                except:
                    error("couldn't clear screen in Screen::display")
            self.writeTitle(out)
            self.writeBody(out, currLine)
            currLine += NUM_BODY_ROWS
            if currLine < bodyLines: # more lines
                self.writeOptions(out, []) # just print empty options box
                input("press enter or return to continue")

        self.writeOptions(out, self.options)
        if len(self.options) > 0:
            pass
            #input("Choose an option:")
        else:
            input("press enter or return to continue")

    def writeTitle(self, out):
        output(BORDER * SCREEN_COLS, file=out)
        output(CenterAlignedRow(self.title), file=out)
        output(BORDER * SCREEN_COLS, file=out)

    """
    Writes the body lines within [firstLineNum, firstLineNum + NUM_BODY_ROWS)
    """
    def writeBody(self, out, firstLineNum=0):
        output(BORDER * SCREEN_COLS, file=out)
        self.writeOneCol(out, firstLineNum)
        output(BORDER * SCREEN_COLS, file=out)

    def writeOneCol(self, out, firstLineNum=0):
        rowNum = 0
        row = None
        while rowNum < NUM_BODY_ROWS:
            if rowNum + firstLineNum < len(self.body):
                row = self.body[rowNum + firstLineNum]
                output(row, file=out)
            else:
                output(f'{BORDER} {" " * (SCREEN_COLS - 4)} {BORDER}', file=out)
            rowNum = rowNum + 1

    def writeOptions(self, out, options):
        output(BORDER * SCREEN_COLS, file=out)

        options = [str(option) for option in options]

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
            output(f'{BORDER} {msg} {BORDER}', file=out)

        output(BORDER * SCREEN_COLS, file=out)

    def displayAndChoose(self, prompt: str)->"any":
        self.display()
        return choose(prompt, self.options, False)


"""
Psuedo-abstract class
"""
class RowStyle:
    def format(self, msg: str)->"list<str>":
        pass

"""
RowContentStyle(n).format(s) will return an array of string each exactly n
characters long
"""
class RowContentStyle(RowStyle):
    def __init__(self, rowWidth):
        super().__init__()
        self.rowWidth = rowWidth

    def wrap(self, msg: str)->"list<str>":
        lines = []
        line = msg.replace("\t", " " * 4)
        if len(line.strip()) is 0: # catch purposely empty lines
            lines.append(line)

        while len(line.strip()) is not 0:
            wordBreak = line.rfind(" ", 0, self.rowWidth)
            firstNonSpace = re.search("[^ ]", line)
            indentation = 0 if not firstNonSpace else firstNonSpace.start()
            if len(line) < self.rowWidth: # fits
                lines.append(line)
                line = indentation * " " + line[self.rowWidth:]
            elif wordBreak < indentation: # no suitable break point
                lines.append(line[:self.rowWidth])
                line = indentation * " " + line[self.rowWidth:]
            else:
                lines.append(line[:wordBreak])
                line = indentation * " " + line[(wordBreak + 1):]

        return lines

    def format(self, msg: str)->"list<str>":
        rows = []
        msg = msg.replace("\t", " " * 4)

        for line in msg.split("\n"):
            rows.extend(self.wrap(line))

        return [row.ljust(self.rowWidth) for row in rows]

class BorderedRowStyle(RowStyle):
    def __init__(self, rowWidth=SCREEN_COLS, border="#", padding=" "):
        super().__init__()
        self.border = border
        self.padding = padding
        bodyWidth = rowWidth - (len(border) + len(padding)) * 2
        self.contentStyler = RowContentStyle(bodyWidth)

    def format(self, msg: str)->"list<str>":
        innerStyling = self.contentStyler.format(msg)
        return [f'{self.border}{self.padding}{row}{self.padding}{self.border}' for row in innerStyling]

class SplitRowStyle(RowStyle):
    def __init__(self, rowWidth=SCREEN_COLS, border="#", padding=" "):
        super().__init__()
        self.leftStyle = BorderedRowStyle(math.floor(rowWidth / 2), border, padding)
        self.rightStyle = BorderedRowStyle(math.ceil(rowWidth / 2), border, padding)

    def format(self, left, right)->"list<str>":
        rows = []

        leftRows = self.leftStyle.format(left)
        rightRows = self.rightStyle.format(right)

        # Pair up left and right rows. Rows with no match get paired with spaces
        numRows = max(len(leftRows), len(rightRows))
        for i in range(numRows):
            l = self.leftStyle.format(" ")[0] # empty row
            r = self.rightStyle.format(" ")[0]
            if len(leftRows) > i:
                l = leftRows[i]
            if len(rightRows) > i:
                r = rightRows[i]
            rows.append(f'{l}{r}')

        return rows

class BodyRow:
    def __init__(self, content: str):
        self.content = content

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
