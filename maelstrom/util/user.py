"""
This module replaces the old distinction between player and AI teams
"""



from util.serialize import AbstractJsonSerialable # old util package



class User(AbstractJsonSerialable):
    """
    A User simply contains a name, team, and inventory.
    Future versions will also store campaign info and other choices in this
    """

    def __init__(self, **kwargs):
        """
        required kwargs:
        - name: str
        - members: list of AbstractCharacters
        - inventory: list of Items (defaults to [])
        """
        super().__init__(**dict(kwargs, type="User"))
        self.name = kwargs[name]
        self.members = kwargs[members]
        self.inventory = kwargs.get(inventory, [])
