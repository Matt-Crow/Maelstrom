from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    """
    Configuration options that determine how Maelstrom will run
    """

    keep_output: bool = False
    """
    whether to clear the screen before outputting a new menu
    """

    test: bool = False
    """
    whether to test or run
    """