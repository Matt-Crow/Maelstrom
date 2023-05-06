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