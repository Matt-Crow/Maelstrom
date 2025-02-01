"""
Specifies which template to use when constructing a character,
and other details which differentiate them from other characters made by the template.

For example, two Alexandre's may use the same template, but can have different levels.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CharacterSpecification:
    """
    Combined with a CharacterTemplate to make a Character
    """

    name: str
    """
    The name of the template to use
    """

    level: int = 1

    xp: int = 0

    active_names: list[str] = field(default_factory=list)
    """
    The names of the character's active abilities
    """

    def to_dict(self) -> dict:
        """
        Converts to a dictionary for JSON serialization
        """
        json = dict(
            name=self.name,
            level=self.level,
            xp=self.xp,
            active_names=self.active_names
        )
        return json

# can't be static method - CharacterSpecification was not defined
def json_dict_to_character_specification(json: dict) -> CharacterSpecification:
    spec = CharacterSpecification(
        name=json["name"],
        level=json["level"],
        xp=json["xp"],
        active_names=json["active_names"]
    )
    return spec