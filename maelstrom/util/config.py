"""
Configuration data
"""

from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    """
    Configuration options that determine how Maelstrom will run
    """

    debug: bool = False
    """
    whether to print debug output
    """

    keep_output: bool = False
    """
    whether to clear the screen before outputting a new menu
    """

    test: bool = False
    """
    whether to test or run
    """

_global_config = Config()
"""
Do not reference this variable directly, use set_global_config and 
get_global_config instead

The current configuration Maelstrom is using.

The program currently has many references to a global configuration,
and while global variables are not ideal, it may take time to convert to
non-global references.
"""

def set_global_config(new_global_config: Config):
    """
    overrides the current configuration - all references to the global config
    will now point to the new one
    """
    global _global_config
    _global_config = new_global_config

def get_global_config() -> Config:
    """
    use this to access the globally configured options
    """
    return _global_config