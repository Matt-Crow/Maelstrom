"""
This module contains code related to the user interface.
This code is abstract so it can be implemented by both a command-line interface and graphical user interfaces.

TODO Might be better with just a single data class such as

ScreenDataInfo:
    title: str
    left_scoreboard: list[str]
    right_scoreboard: list[str]
    body: list[str]
    prompt: str
    choice: AbstractChoice

And an abstract class such as

class AbstractUserInterface(ABC):
    @abstractmethod
    def display(self, screen: ScreenDataInfo):
        pass
"""

from abc import ABC, abstractmethod

from maelstrom.choices import AbstractChoice


class AbstractUserInterface(ABC):
    """
    A user interface is something which can display output to a user and receive input from them.
    """

    @property
    @abstractmethod
    def title(self) -> str:
        """
        Should be displayed somewhere on the UI.
        Tells the user what the current screen is about.
        """
        pass
    
    @title.setter
    @abstractmethod
    def title(self, value: str):
        """
        Sets a new title for the UI.
        """
        pass

    @abstractmethod
    def add_scoreboard_row(self, left: str, right: str):
        """
        Adds text to the left and right sections of the UI.
        These areas are known as the Scoreboard.
        """
        pass

    @abstractmethod
    def add_body_row(self, row: str):
        """
        Adds text to the body of the UI.
        """
        pass

    @abstractmethod
    def add_body_rows(self, rows: list[str]):
        """
        Adds multiple lines of text to the body of the UI.
        """
        pass

    @abstractmethod
    def clear(self):
        """
        Removes all content from the UI.
        """
        pass

    @abstractmethod
    def display(self):
        """
        Displays the UI and waits for user input.
        TODO add callback
        """
        pass

    @abstractmethod
    def display_choice(self, prompt: str, choice: AbstractChoice):
        """
        Displays the UI and presents a choice to the user.
        """
        pass