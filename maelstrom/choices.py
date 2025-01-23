"""
This module handles user choices
"""

class Choice[T]:
    """
    A choice between one of several options.
    """

    def __init__(self, prompt: str, options: list[T]):
        self._prompt = prompt
        self._options = options
    
    @property
    def prompt(self) -> str:
        """
        The prompt to tell the user what they are choosing.
        """
        return self._prompt

    @property
    def options(self) -> list[T]:
        """
        The different options which the user can choose from.
        """
        return self._options
    