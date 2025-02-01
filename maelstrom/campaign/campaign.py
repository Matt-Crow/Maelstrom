"""
A campaign is a collection of story elements and challenges the player can
overcome.

Each player will keep track of the campaign they are playing and their various
statistics within that campaign, such as which levels they have won or lost.
"""
from maelstrom.campaign.area import Area

class Campaign:
    def __init__(self, **kwargs):
        """
        Required kwargs:
        - name: str
        - areas: list[Area]
        """
        self.name = kwargs["name"]
        self.areas = kwargs.get("areas", [])

    def get_area(self, num: int) -> Area:
        return self.areas[num]