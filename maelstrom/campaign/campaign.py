"""
A campaign is a collection of story elements and challenges the player can
overcome.

Each player will keep track of the campaign they are playing and their various
statistics within that campaign, such as which levels they have won or lost.
"""
from maelstrom.campaign.area import Area
from maelstrom.util.serialize import AbstractJsonSerialable


class Campaign(AbstractJsonSerialable):

    def __init__(self, **kwargs):
        """
        Required kwargs:
        - name: str
        - areas: list[Area]
        """
        super().__init__(**dict(kwargs, type="Campaign"))
        self.name = kwargs["name"]
        self.areas = kwargs.get("areas", [])
        self.addSerializedAttributes("name", "areas")

    def get_area(self, num: int) -> Area:
        return self.areas[num]