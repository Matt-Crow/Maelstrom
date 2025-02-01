"""
This module handles teams - collections of Characters
"""

from typing import Callable
from maelstrom.dataClasses.character import Character
import functools

class Team:
    """
    stores and manages Characters
    """

    def __init__(self, name: str, members: list[Character]):
        self.name = name
        self.members = []
        self.membersRemaining = []
        for member in members:
            self.addMember(member)

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

    def init_for_battle(self):
        """
        this method must be called at the start of each Battle
        """
        self.membersRemaining.clear()
        for member in self.members: # can't use lambda with "each" here
            member.init_for_battle()
            self.membersRemaining.append(member)
        self.updateMembersRemaining() # updates ordinals

    def isDefeated(self)->bool:
        return len(self.membersRemaining) == 0

    def updateMembersRemaining(self)->list[str]:
        msgs = []

        newList = []
        nextOrdinal = 0 # records which index of the array each member is in
        for member in self.membersRemaining:
            if member.is_koed():
                msgs.append(f'{member.name} is out of the game!')
            else:
                newList.append(member)
                member.ordinal = nextOrdinal
                nextOrdinal += 1
                member.update()
        self.membersRemaining = newList

        return msgs
