"""
this module will eventually include a Campaign class - a collection of Areas
"""



from util.serialize import AbstractJsonSerialable



class Location(AbstractJsonSerialable):
    """
    Locations provide flavor text for an Area
    """

    def __init__(self, **kwargs):
        """
        required kwargs:
        - name: str
        - description: str
        """
        super().__init__(**dict(kwargs, type="Location"))
        self.name = kwargs["name"]
        self.description = kwargs["description"]
        self.addSerializedAttributes("name", "description")

    def __str__(self)->str:
        return f'Area {self.name}'

    def getDisplayData(self)->str:
        """
        gets data to output
        """
        return f'{self.name}: "{self.description}"'
