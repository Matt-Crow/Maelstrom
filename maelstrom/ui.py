"""
This module contains code related to the user interface.
This code is abstract so it can be implemented by both a command-line interface and graphical user interfaces.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

@dataclass(frozen=True)
class Choice[T]:
    """
    A choice between one of several options.
    """

    prompt: str
    """
    Tells the user what they are choosing.
    """

    options: list[T] = field(default_factory=list)
    """
    The different options which the user can choose from.
    """

@dataclass
class Screen:
    """
    Information to display to the user
    """

    title: str = "Maelstrom"
    """
    Tells the user what this screen is about
    """

    left_scoreboard: list[str] = field(default_factory=list)
    """
    Text shown on the left side of the screen
    """

    right_scoreboard: list[str] = field(default_factory=list)
    """
    Text shown on the right side of the screen
    """

    body_rows: list[str] = field(default_factory=list)
    """
    Text shown below the scoreboards
    """

    choice: Optional[Choice] = None
    """
    The choice the user has to make on this screen, if any.
    """

class AbstractUserInterface(ABC):
    """
    A user interface is something which can display output to a user and receive input from them.
    """

    @abstractmethod
    async def display_and_choose(self, screen: Screen) -> any:
        """
        Displays the given screen and asks the user to make a choice.
        Returns an async thing which resolves once the user makes a choice.
        """
        pass