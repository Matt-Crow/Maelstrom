"""
Input-output utilities
* StandardInputChannel
* StandardOutputChannel
* Chooser
"""

from abc import ABC, abstractmethod


class InputChannel(ABC):
    """
    Requests input from some input source.
    Subclasses must override the `read` method.
    """

    @abstractmethod
    def read(self)->str:
        pass

    def read_int(self)->int:
        return int(float(self.read()))

class ListInputChannel(InputChannel):
    """
    Consumes input from a list of strings
    """

    def __init__(self, inputs=[]):
        super().__init__()
        self._inputs = inputs.copy()

    def read(self)->str:
        if len(self._inputs) == 0:
            raise IndexError('No more inputs to read')
        return self._inputs.pop()

class StandardInputChannel(InputChannel):
    """
    Consumes input from stdin
    """
    def read(self) -> str:
        return input()


class OutputChannel(ABC):
    """
    Writes output.
    Subclasses must override the `write` method.
    """        

    @abstractmethod
    def write(self, *args, **kwargs):
        pass

class DevNullOutputChannel(OutputChannel):
    """
    Does not write output anywhere
    """

    def write(self, *args, **kwargs):
        pass # goes nowhere, does nothing

class ListOutputChannel(OutputChannel):
    """
    Saves messages it receives
    """

    def __init__(self):
        super().__init__()
        self._messages = []
    
    def write(self, *args, **kwargs):
        self._messages.append([arg for arg in args])

class StandardOutputChannel(OutputChannel):
    """
    Writes output to stdout
    """

    def write(self, *args, **kwargs):
        return print(*args, **kwargs)

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