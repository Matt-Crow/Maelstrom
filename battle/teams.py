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
        - type : str
        - name : str
        - members : list of AbstractCharacters
        """
        super().__init__(**dict(kwargs, type=kwargs["type"]))
        self.name = kwargs["name"]
        self.members = []
        for member in kwargs["members"]:
            self.addMember(member)
        self.membersRem = self.members
        self.enemy = None
        self.addSerializedAttributes(
            "name",
            "members"
        )

    """
    Use this to access team members
    """
    def getMember(self, num=0)->"AbstractCharacter":
        return self.members[num]

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
        for member in self.membersRem:
            if not member.isKoed():
                newMembersRem.append(member)
                member.update()
            else:
                msgs.append(f'{member.name} is out of the game!')
        self.membersRem = newMembersRem

    def isDefeated(self):
        """
        Use to see if your team still exists
        """
        return len(self.membersRem) == 0


    def initForBattle(self):
        # I will definitely want to add a forEach sort of method
        self.membersRem = []
        for member in self.members:
            member.initForBattle()
            self.membersRem.append(member)

    def displayShortDescription(self):
        screen = Screen()
        screen.setTitle(f'Team: {self.name}')
        displayData = self.getShortDisplayData()
        screen.addBodyRow(displayData)
        screen.display()

    """
    This method gives a brief overview of this team. Used for the battle UI
    """
    def getShortDisplayData(self)->str:
        lines = [
            f'{self.name}:'
        ]
        longestName = lengthOfLongest((member.name for member in self.membersRem))
        longestHp = lengthOfLongest((str(member.remHp) for member in self.membersRem))
        for member in self.membersRem:
            lines.append(f'* {member.name.ljust(longestName)}: {str(member.remHp).rjust(longestHp)} HP')
        return "\n".join(lines)

    def display(self):
        screen = Screen()
        screen.setTitle(f'Team: {self.name}')
        displayData = self.getDisplayData()
        screen.addBodyRow(displayData)
        screen.display()

    def getDisplayData(self)->str:
        """
        This provides a more descriptive overview of the team, detailing all of its
        members. It feels a little info-dump-y, so it feels tedious to scroll
        through. Do I want some other way of providing players with team data?
        """

        lines = [
            f'{self.name}:'
        ]
        for member in self.members:
            lines.append(member.getDisplayData())

        return "\n".join(lines)

    def __str__(self):
        return self.name



class PlayerTeam(AbstractTeam):
    """
    Required kwargs:
    - name : str
    - member : PlayerCharacter
    """
    def __init__(self, **kwargs):
        super(PlayerTeam, self).__init__(**dict(kwargs, type="PlayerTeam", members=[kwargs["member"]]))

class EnemyTeam(AbstractTeam):
    """
    Required kwargs:
    - name : str,
    - members : list of EnemyCharacters
    """
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**dict(kwargs, type="EnemyTeam"))
