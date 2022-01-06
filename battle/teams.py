"""
Teams are used to group characters
together so that the program knows
who are enemies, and who are allies.
"""



from util.serialize import AbstractJsonSerialable
from util.stringUtil import lengthOfLongest
from inputOutput.screens import Screen



class AbstractTeam(AbstractJsonSerialable):

    def __init__(self, **kwargs):
        """
        Required kwargs:
        - name : str
        - members : list of AbstractCharacters
        """
        super().__init__(**dict(kwargs, type="Team"))
        self.name = kwargs["name"]
        self.members = []
        for member in kwargs["members"]:
            self.addMember(member)
        self.membersRemaining = self.members
        self.enemy = None
        self.addSerializedAttributes(
            "name",
            "members"
        )

    """
    Adds a character to this' team, if they are not
    already on the team
    """
    def addMember(self, member: 'AbstractCharacter'):
        if member not in self.members:
            self.members.append(member)
            member.team = self

    """
    How much xp will be given
    once this team is
    defeated.
    """
    # balance this later
    def getXpGiven(self):
        xp = 0
        for member in self.members:
            xp += member.level * 10
        return xp / len(self.members)

    """
    Updates the members remaining on the team, and appends to a list of messages
    to display
    """
    def updateMembersRem(self, msgs):
        newMembersRem = []
        for member in self.membersRemaining:
            if not member.isKoed():
                newMembersRem.append(member)
                member.update()
            else:
                msgs.append(f'{member.name} is out of the game!')
        self.membersRemaining = newMembersRem

    def isDefeated(self):
        """
        Use to see if your team still exists
        """
        return len(self.membersRemaining) == 0


    def initForBattle(self):
        # I will definitely want to add a forEach sort of method
        self.membersRemaining = []
        for member in self.members:
            member.initForBattle()
            self.membersRemaining.append(member)

    def __str__(self):
        return self.name
