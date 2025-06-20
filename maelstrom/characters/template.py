from dataclasses import dataclass

@dataclass(frozen=True)
class CharacterTemplate:
    """
    A CharacterTemplate provides the data a Character is based on.
    Each stat should be between 1 and 5 stars
    """

    name: str
    """
    a unique identifier for this character
    """

    element: str
    """
    case insensitive - might make enum later
    """

    type: str = ""
    """
    discriminator column to distinguish between starters and enemies
    """

    control: int = 3
    """
    base control stat
    might make these percentages later
    """
    
    resistance: int = 3
    """
    base resistance stat
    """

    potency: int = 3
    """
    base potency stat
    """
    
    luck: int = 3
    """
    base luck stat
    """

    energy: int = 3
    """
    base energy stat
    """