"""
This module provides the basic structure of the screens the program displays

Primary export:

* Class Screen
    - add_body_rows(list[str])
    - add_body_row(str)
    - add_split_row(str, str)
    - display(list[any])
    - display_and_choose(str, AbstractChoice)
"""

import math
import re
import subprocess
from maelstrom.choices import AbstractChoice
from maelstrom.inputOutput.output import output, error
from maelstrom.io import Chooser
from maelstrom.util.stringUtil import lengthOfLongest
from maelstrom.util.config import get_global_config

SCREEN_COLS = 80
BORDER = "#"
OPTION_ROWS = 5
NUM_BODY_ROWS = 10

class Screen:
    def __init__(self, title: str = "Maelstrom"):
        """
        Creates a screen with the given title.
        """
        self._title = title
        self._body = [] # list[str]

    def add_body_rows(self, rows: list[str]):
        """
        Adds the given rows to the body of the screen.
        """
        for row in rows:
            self.add_body_row(row)

    def add_body_row(self, row: str):
        """
        Adds the given row to the body of the screen.
        """
        self._body.extend(_format_bordered_row(str(row)))

    def add_split_row(self, left: str, right: str):
        """
        Adds a row to the screen where the left half is the first parameter and the right half is the second parameter.
        """
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
            self._body.append(f'{l}{r}')

    def display(self, options=[]):
        """
        Displays the screen and optionally some options.
        """
        num_pages = int(len(self._body) / NUM_BODY_ROWS)
        if num_pages == 0:
            num_pages = 1 # show at least 1 page
        for page in range(num_pages):
            self._write_body_page(page)
            if page != num_pages - 1: # more pages
                self._write_options([]) # just print empty options box
                input("press enter or return to continue")

        # allow player to choose once we're done displaying the body
        self._write_options(options)
        if len(options) == 0:
            input("press enter or return to continue")
    
    def display_and_choose(self, prompt: str, choice: AbstractChoice):
        """
        Asks the user to make the given choice.
        """
        self.display(choice.options)
        user_choice = Chooser().choose(prompt, choice.options, False)
        choice.handle_chosen(user_choice)

    def _write_body_page(self, page: int):
        if not get_global_config().keep_output:
            try:
                works = subprocess.call("cls", shell=True)
                if works != 0: # is false, didn't run
                    works = subprocess.call("clear", shell=True)
            except:
                error("couldn't clear screen")
        
        # write the title
        self._write_horizontal_line()
        centered_title_width = SCREEN_COLS - len(BORDER + " ") * 2
        centered_title = self._title.center(centered_title_width)
        centered_title_row = f'{BORDER} {centered_title} {BORDER}'
        output(centered_title_row)
        self._write_horizontal_line()    

        # write this page of the body
        curr_line_num = page * NUM_BODY_ROWS
        self._write_horizontal_line()
        for _ in range(NUM_BODY_ROWS):
            if curr_line_num < len(self._body):
                row = self._body[curr_line_num]
            else:
                row = f'{BORDER} {" " * (SCREEN_COLS - 4)} {BORDER}'
            output(row)
            curr_line_num += 1
        self._write_horizontal_line()

    def _write_horizontal_line(self):
        output(BORDER * SCREEN_COLS)

    def _write_options(self, options):
        self._write_horizontal_line()

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
            output(f'{BORDER} {msg} {BORDER}')

        self._write_horizontal_line()

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