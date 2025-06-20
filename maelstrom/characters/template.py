from dataclasses import dataclass

@dataclass(frozen=True)
class CharacterTemplate:
    """
    A CharacterTemplate provides the data a Character is based on
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

    control: int = 0
    """
    base control stat
    might make these percentages later
    """
    
    resistance: int = 0
    """
    base resistance stat
    """

    potency: int = 0
    """
    base potency stat
    """
    
    luck: int = 0
    """
    base luck stat
    """

    energy: int = 0
    """
    base energy stat
    """