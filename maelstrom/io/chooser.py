"""
Allows the user to choose from lists of options
"""

from maelstrom.io.input import InputChannel, StandardInputChannel
from maelstrom.io.output import OutputChannel, StandardOutputChannel


class Chooser:
    """
    Allows the user to choose from a list of options
    """

    def __init__(self, input: InputChannel = None, output: OutputChannel = None):
        """
        input and output default to stdin and stdout respectively
        """
        if input is None:
            input = StandardInputChannel()
        if output is None:
            output = StandardOutputChannel()
        self._input = input
        self._output = output
    
    def choose(self, prompt: str, options: 'list[any]', display_options=True)->'any':
        options = to_list(options)
        chosen = options[0] # purposely fails if no options

        if len(options) > 1: # only ask if user has a choice
            self._output.write(prompt)
            if display_options:
                names = [str(option) for option in options]
                for i in range(0, len(names)):
                    self._output.write(f'{i + 1}: {names[i]}')
            
            idx = -1
            while idx < 0 or len(options) <= idx: # ask until valid
                self._output.write(f'Enter a number [1 - {len(options)}]: ', end='')
                try:
                    idx = self._input.read_int() - 1 # move from 1-index to 0-index
                except ValueError:
                    pass # user entered non-number
            chosen = options[idx]
            
        return chosen

def to_list(obj: any) -> 'list[any]':
    """
    converts input to a list, if it is not one already
    """
    as_list = []
    try:
        for i in iter(obj):
            as_list.append(i)
    except TypeError:
        as_list.append(obj)
    return as_list