"""
This module handles teams - collections of Characters
"""



from typing import Callable
from maelstrom.dataClasses.character import Character
from maelstrom.util.serialize import AbstractJsonSerialable
import functools



class Team(AbstractJsonSerialable):
    """
    stores and manages Characters
    """

    def __init__(self, **kwargs):
        """
        Required kwargs:
        - name: str
        - members: list of Characters. Expects at least 1 member
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

    def addMember(self, member: Character):
        if member in self.members:
            raise Exception(f'cannot add duplicate member {str(member)}')
        member.team = self
        self.members.append(member)
        self.membersRemaining.append(member)

    def getXpGiven(self)->int:
        """
        provides how much XP this Team provides when encountered
        """
        totalLevel = functools.reduce(lambda xp, member: member.level + xp, self.members, 0)
        return int(10 * totalLevel / len(self.members))

    def eachMember(self, consumer: Callable[[Character], None]):
        """
        calls the given consumer on each member of this Team
        """
        for member in self.members:
            consumer(member)

    def eachMemberRemaining(self, consumer: Callable[[Character], None]):
        """
        calls the given consumer on each member of this Team who isn't out of
        the game
        """
        for member in self.membersRemaining:
            consumer(member)

    def getMembersRemaining(self)->list[Character]:
        """
        returns a shallow copy of this Team's remaining members
        """
        return [member for member in self.membersRemaining]

    def initForBattle(self):
        """
        this method must be called at the start of each Battle
        """
        self.membersRemaining.clear()
        for member in self.members: # can't use lambda with "each" here
            member.initForBattle()
            self.membersRemaining.append(member)
        self.updateMembersRemaining() # updates ordinals

    def isDefeated(self)->bool:
        return len(self.membersRemaining) == 0

    def updateMembersRemaining(self)->list[str]:
        msgs = []

        newList = []
        nextOrdinal = 0 # records which index of the array each member is in
        for member in self.membersRemaining:
            if member.isKoed():
                msgs.append(f'{member.name} is out of the game!')
            else:
                newList.append(member)
                member.ordinal = nextOrdinal
                nextOrdinal += 1
                member.update()
        self.membersRemaining = newList

        return msgs
