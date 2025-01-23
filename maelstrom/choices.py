"""
This module handles user choices
"""

from abc import abstractmethod

class AbstractChoice:
    """
    Represents a choice a user can make.
    """

    @property
    @abstractmethod
    def prompt(self) -> str:
        """
        The prompt to tell the user what they are choosing.
        """
        pass

    @property
    @abstractmethod
    def options(self) -> list[any]:
        """
        The different options which the user can choose from.
        """
        pass

class ChooseOneOf[T]:
    """
    A choice between one of several options.
    """

    def __init__(self, prompt: str, options: list[T]):
        self._prompt = prompt
        self._options = options
    
    @property
    def prompt(self) -> str:
        return self._prompt

    @property
    def options(self) -> list[T]:
        return self._options
    
class ChooseOneOrNone[T, U]:
    """
    A choice between one of several options, or "none of these".
    """

    def __init__(self, prompt: str, options: list[T], none_of_these: U):
        self._prompt = prompt
        self._options = options
        self._none_of_these = none_of_these
    
    @property
    def prompt(self) -> str:
        return self._prompt
    
    @property
    def options(self) -> list[any]:
        result = self._options.copy()
        result.append(self._none_of_these)
        return result
    