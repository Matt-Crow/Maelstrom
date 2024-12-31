"""
This module handles user choices
"""

from abc import abstractmethod
from dataclasses import dataclass
from typing import Callable

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

    @abstractmethod
    def handle_chosen(self, chosen: any):
        """
        Call this method with the user's choice after they have chosen one.
        """
        pass

class ChooseOneOf[T]:
    """
    A choice between one of several options.
    """

    def __init__(self, prompt: str, options: list[T], callback: Callable[[T], None]):
        self._prompt = prompt
        self._options = options
        self._callback = callback
    
    @property
    def prompt(self) -> str:
        return self._prompt

    @property
    def options(self) -> list[T]:
        return self._options
    
    def handle_chosen(self, chosen: T):
        self._callback(chosen)

class ChooseOneOrNone[T, U]:
    """
    A choice between one of several options, or "none of these".
    """

    def __init__(self, prompt: str, options: list[T], none_of_these: U, handle_choice: Callable[[T], None], handle_none: Callable[[], None]):
        self._prompt = prompt
        self._options = options
        self._none_of_these = none_of_these
        self._handle_choice = handle_choice
        self._handle_none = handle_none
    
    @property
    def prompt(self) -> str:
        return self._prompt
    
    @property
    def options(self) -> list[any]:
        result = self._options.copy()
        result.append(self._none_of_these)
        return result
    
    def handle_chosen(self, chosen: any):
        if chosen is self._none_of_these:
            self._handle_none()
        else:
            self._handle_choice(chosen)

@dataclass(frozen=True)
class ActionMapping:
    """
    Maps text to an action
    """

    text: str
    """
    The text to display to users
    """

    action: Callable[[], None]
    """
    The action to call when the user chooses the text
    """

class ChooseAction:
    """
    Maps choices to actions
    """

    def __init__(self, prompt: str, action_mappings: list[ActionMapping]):
        self._prompt = prompt
        self._action_mappings = action_mappings # needs to be ordered
    
    @property
    def prompt(self) -> str:
        return self._prompt

    @property
    def options(self) -> list[str]:
        return [m.text for m in self._action_mappings]
    
    def handle_chosen(self, chosen: str):
        try:
            action = next((m.action for m in self._action_mappings if m.text == chosen))
            action()
        except StopIteration:
            raise ValueError(f'Invalid choice: "{chosen}"')
