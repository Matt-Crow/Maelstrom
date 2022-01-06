"""
This module handles teams - collections of AbstractCharacters
"""



from util.serialize import AbstractJsonSerialable # old util package
import functools



class Team(AbstractJsonSerialable):
    """
    stores and manages AbstractCharacters
    """

    def __init__(self, **kwargs):
        """
        Required kwargs:
        - name: str
        - members: list of AbstractCharacters. Expects at least 1 member
        """
        super().__init__(**dict(kwargs, type="Team"))
        self.name = kwargs["name"]
        self.members = []
        self.membersRemaining = []
        for member in kwargs["members"]:
            self.addMember(member)
        self.addSerializedAttributes("name", "members")

    def __str__(self):
        return self.name

    def addMember(self, member: "AbstractCharacter"):
        if member in self.members:
            raise Exception(f'cannot add duplicate member {str(member)}')
        self.members.append(member)
        self.membersRemaining.append(member)

    def getXpGiven(self)->int:
        """
        provides how much XP this Team provides when encountered
        """
        totalLevel = functools.reduce(lambda xp, member: member.level + xp, self.members)
        return int(10 * totalLevel / len(self.members))

    def eachMember(self, consumer: "function(AbstractCharacter)"):
        """
        calls the given consumer on each member of this Team
        """
        for member in self.members:
            consumer(member)

    def eachMemberRemaining(self, consumer: "function(AbstractCharacter)"):
        """
        calls the given consumer on each member of this Team who isn't out of
        the game
        """
        for member in self.membersRemaining:
            consumer(member)

    def initForBattle(self):
        """
        this method must be called at the start of each Battle
        """
        self.membersRemaining.clear()
        for member in self.members: # can't use lambda with "each" here
            member.initForBattle()
            self.membersRemaining.append(member)

    def isDefeated(self)->bool:
        return len(self.membersRemaining) == 0

    def updateMembersRemaining(self)->"List<str>":
        msgs = []
        newList = []
        for member in self.membersRemaining:
            if member.isKoed():
                msgs.append(f'{member.name} is out of the game!')
            else:
                newList.append(member)
                member.update()
        self.membersRemaining = newList
        return msgs
