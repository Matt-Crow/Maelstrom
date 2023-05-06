"""
Writes output to the user.
"""

from abc import ABC, abstractmethod

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