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

import math
import sys
import re
import subprocess
from maelstrom.inputOutput.output import output, error
from maelstrom.io import Chooser
from maelstrom.util.stringUtil import lengthOfLongest
from maelstrom.util.config import get_global_config

SCREEN_COLS = 80
BORDER = "#"
OPTION_ROWS = 5
NUM_BODY_ROWS = 10
CHOOSER = Chooser()

def choose(prompt: str, options: list[any], displayOptions=True)->"any":
    return CHOOSER.choose(prompt, options, displayOptions)

class Screen:
    def __init__(self):
        self.title = "Maelstrom"
        self.body = [] # List of str
        self.options = []

    def setTitle(self, title: str):
        self.title = title[:(SCREEN_COLS - 4)] # ensures title fits

    def addBodyRows(self, rows: list[str]):
        for row in rows:
            self.addBodyRow(row)

    def addBodyRow(self, row: str):
        if type(row) == type("Hello world!"):
            self.body.extend(_format_bordered_row(row))
        else: # check if iterable AFTER checking if string
            try: # https://stackoverflow.com/questions/1952464/in-python-how-do-i-determine-if-an-object-is-iterable
                for item in iter(row):
                    self.body.extend(_format_bordered_row(item))
            except TypeError: # neither str nor iterable
                self.body.extend(_format_bordered_row(str(row)))

    def addSplitRow(self, left: str, right: str):
        def style_left(content: str):
            return _format_bordered_row(content, math.floor(SCREEN_COLS / 2))
        def style_right(content: str):
            return _format_bordered_row(content, math.ceil(SCREEN_COLS / 2))
        left_rows = style_left(left)
        right_rows = style_right(right)

        # Pair up left and right rows. Rows with no match get paired with spaces
        num_rows = max(len(left_rows), len(right_rows))
        for i in range(num_rows):
            l = style_left(" ")[0] # empty row
            r = style_right(" ")[0]
            if len(left_rows) > i:
                l = left_rows[i]
            if len(right_rows) > i:
                r = right_rows[i]
            self.body.append(f'{l}{r}')

    """
    There may need to be some limit on the number of options this can be given
    """
    def addOption(self, option: "any"):
        self.options.append(option)

    def clear(self):
        self.title = "Maelstrom"
        self.clearBody()
        self.clearOptions()

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
            if not get_global_config().keep_output:
                try:
                    works = subprocess.call("cls", shell=True)
                    if works != 0: #is false, didn't run
                        works = subprocess.call("clear", shell=True)
                except:
                    error("couldn't clear screen in Screen::display")
            self.writeTitle(out)
            self.writeBody(out, 0) # print blank body

        while currLine < bodyLines:
            if not get_global_config().keep_output:
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
        
        # center-align the title
        centered_title_width = SCREEN_COLS - len(BORDER + " ") * 2
        centered_title = self.title.center(centered_title_width)
        centered_title_row = f'{BORDER} {centered_title} {BORDER}'
        output(centered_title_row, file=out)
        
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
                    if colNum != 0:
                        msg += f'{BORDER} ' # separate columns with border
                    msg += f'{(i + 1):2}: {options[i].ljust(colWidths[colNum])}'
            msg = msg.ljust(SCREEN_COLS - 4)[:(SCREEN_COLS - 4)] # justify and trim it to fit exactly
            output(f'{BORDER} {msg} {BORDER}', file=out)

        output(BORDER * SCREEN_COLS, file=out)

    def displayAndChoose(self, prompt: str)->"any":
        self.display()
        return choose(prompt, self.options, False)

def _format_bordered_row(content: str, width: int = SCREEN_COLS) -> list[str]:
    rows = []
    content = content.replace("\t", " " * 4)
    for line in content.split("\n"):
        rows.extend(_wrap(line, width))
    return [f'{BORDER} {row.ljust(width - 4)} {BORDER}' for row in rows]

def _wrap(msg: str, width: int) -> list[str]:
    lines = []
    line = msg.replace("\t", " " * 4)
    if len(line.strip()) == 0: # catch purposely empty lines
        lines.append(line)

    while len(line.strip()) != 0:
        wordBreak = line.rfind(" ", 0, width)
        firstNonSpace = re.search("[^ ]", line)
        indent = 0 if not firstNonSpace else firstNonSpace.start()
        take = -1
        if len(line) < width: # fits
            take = width
        elif wordBreak < indent: # no suitable break point
            take = width
        else:
            take = wordBreak + 1
        lines.append(line[:take])
        line = line[take:].rjust(indent)

    return lines