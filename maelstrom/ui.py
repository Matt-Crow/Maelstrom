"""
This module contains code related to the user interface.
This code is abstract so it can be implemented by both a command-line interface and graphical user interfaces.

TODO Might be better with just a single data class such as
    prompt: str
    choice: AbstractChoice
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from maelstrom.choices import AbstractChoice

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

    choice: Optional[AbstractChoice] = None
    """
    The choice the user has to make on this screen, if any.
    """

class AbstractUserInterface(ABC):
    """
    A user interface is something which can display output to a user and receive input from them.
    """

    @abstractmethod
    def display(self, screen: Screen):
        """
        Displays the given screen and waits for user input.
        TODO add callback
        """
        pass

    @abstractmethod
    def display_choice(self, screen: Screen):
        """
        Displays the UI to the user.
        """
        pass