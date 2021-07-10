from utilities import choose
from character import PlayerCharacter, EnemyCharacter, AbstractCharacter
from item import Item
from serialize import AbstractJsonSerialable
from fileSystem import USER_DIR, saveSerializable, loadSerializable
from util.stringUtil import entab, lengthOfLongest
from characters.stat_classes import Boost
from inputOutput.screens import Screen
import os
import random
from inputOutput.output import debug

"""
Teams are used to group characters
together so that the program knows
who are enemies, and who are allies.
"""
class AbstractTeam(AbstractJsonSerialable):
    """
    Required kwargs:
    - type : str
    - name : str
    - members : list of AbstractCharacters
    """
    def __init__(self, **kwargs):
        super(AbstractTeam, self).__init__(**dict(kwargs, type=kwargs["type"]))
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

    @classmethod
    def deserializeJson(cls, jdict: dict)->"AbstractTeam":
        type = jdict["type"]
        ret = None
        if type == "PlayerTeam":
            jdict["member"] = AbstractCharacter.deserializeJson(jdict["members"][0])
            jdict["inventory"] = [Item.deserializeJson(item) for item in jdict["inventory"]]
            ret = PlayerTeam(**jdict)
        elif type =="EnemyTeam":
            jdict["members"] = [AbstractCharacter.deserializeJson(member) for member in jdict["members"]]
            ret = EnemyTeam(**jdict)
        else:
            raise Error("Type not found for AbstractTeam: {0}".format(type))
        return ret

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
    Updates the members remaining on the team, and returns a list of messages to
    display
    """
    def updateMembersRem(self)->"List<str>":
        msgs = []

        newMembersRem = []
        for member in self.membersRem:
            if not member.isKoed():
                newMembersRem.append(member)
                member.update()
            else:
                msgs.append(f'{member.name} is out of the game!')
        self.membersRem = newMembersRem

        return msgs

    """
    Changes the active member of this team, inflicting a one-turn penalty
    """
    def switchIn(self, member)->str:
        self.active = member
        member.boost(Boost("control", -0.25, 1, "switch in penalty"))
        return f'{self.active.name} is now active'

    """
    Use to see if your team still exists
    """
    def isDefeated(self):
        return len(self.membersRem) == 0

    """
    Detects when you have only one member left
    """
    def oneLeft(self):
        return len(self.membersRem) == 1

    def initForBattle(self):
        # I will definitely want to add a forEach sort of method
        self.membersRem = []
        for member in self.members:
            member.initForBattle()
            self.membersRem.append(member)
        self.active = self.membersRem[0]

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
        if hasattr(self, "active"):
            lines.append(f'Current active: {self.active.name} ({self.active.energy} energy)')
        return "\n".join(lines)

    def display(self):
        screen = Screen()
        screen.setTitle(f'Team: {self.name}')
        displayData = self.getDisplayData()
        screen.addBodyRow(displayData)
        screen.display()

    """
    This provides a more descriptive overview of the team, detailing all of its
    members. It feels a little info-dump-y, so it feels tedious to scroll
    through. Do I want some other way of providing players with team data?
    """
    def getDisplayData(self)->str:
        lines = [
            f'{self.name}:'
        ]
        for member in self.members:
            lines.append(member.getDisplayData())

        return "\n".join(lines)

    def __str__(self):
        return self.name

    """
    Returns whether or not this team
    should change who is active
    """
    def shouldSwitch(self) -> bool:
        raise NotImplementedError('Team method shouldSwitch is abstract')

    """
    This is abstract: each subclass should implement it
    """
    def chooseSwitchin(self) -> 'AbstractCharacter':
        raise NotImplementedError('Team method chooseSwitchin is abstract')



class PlayerTeam(AbstractTeam):
    """
    Required kwargs:
    - name : str
    - member : PlayerCharacter
    - inventory : list of Items, defaults to []
    """
    def __init__(self, **kwargs):
        super(PlayerTeam, self).__init__(**dict(kwargs, type="PlayerTeam", members=[kwargs["member"]]))
        self.inventory = kwargs.get("inventory", [])
        self.addSerializedAttribute("inventory")

    @classmethod
    def loadUser(cls, userName: str)->"PlayerTeam":
        return loadSerializable(userName, USER_DIR, AbstractTeam)

    def save(self):
        saveSerializable(self, USER_DIR)

    """
    Choices are made using these functions
    """
    def shouldSwitch(self) -> bool:
        """
        Asks the user if they want to
        switch before attacking
        """

        return len(self.members) > 1 and choose('Do you want to switch your active character?', ['Yes', 'No']) == 'Yes'

    def chooseSwitchin(self):
        """
        Who will fight?
        """
        choices = []
        for member in self.membersRem:
            if member != self.active:
                choices.append(member)
        self.switch(choose("Who do you want to bring in?", choices))

    """
    Customization options
    """
    def obtain(self, item):
      self.inventory.append(item)

    def get_available_items(self):
        new_array = []
        for item in self.inventory:
            if not item.equipped:
                new_array.append(item)
        return new_array

    """
    Displays the team management menu
    """
    def manage(self):
        screen = Screen()
        screen.setTitle(f'Manage {self.name}')
        options = ["Exit"]
        for member in self.members:
            screen.addBodyRow(member.getDisplayData())
            options.append(member)


        options.reverse()
        for option in options:
            screen.addOption(option)
        managing = screen.displayAndChoose("Who do you wish to manage?")

        if managing is not "Exit":
            managing.manage()

class EnemyTeam(AbstractTeam):
    """
    Required kwargs:
    - name : str,
    - members : list of EnemyCharacters
    """
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**dict(kwargs, type="EnemyTeam"))

    """
    AI stuff
    BENCHIT NEEDS FIX
    general improvements needed
    """
    def shouldSwitch(self):
        """
        First, check if our active can KO
        """
        if self.oneLeft() or self.enemy.active.calcDmgTaken(self.active, self.active.bestActive()) >= self.enemy.active.remHp:
            return False


        """
        Second, check if an ally can KO
        """
        for member in self.membersRem:
            if self.enemy.active.calcDmgTaken(member, member.bestActive()) * 0.75 >= self.enemy.active.remHp:
                return True


        # Default
        return False


    # comment
    def chooseSwitchin(self):
        """
        Used to help the AI
        decide who to switch in
        """

        """
        Can anyone KO?
        """
        can_ko = []
        for member in self.membersRem:
            if self.enemy.active.calcDmgTaken(member, member.bestActive()) * 0.75 >= self.enemy.active.remHp:
                can_ko.append(member)

        debug("These team members can KO:")
        for member in can_ko:
            debug(f'- {member.name}')

        """
        If one person can KO,
        bring them in.
        If nobody can,
        change nothing.
        If someone can KO,
        only use them.
        """
        if len(can_ko) == 1:
            return can_ko[0]
        elif len(can_ko) == 0:
            array = self.membersRem
        else:
            array = can_ko

        rand = random.randint(0, len(array) - 1)
        return array[rand]

    def chooseNewActive(self):
        return self.switchIn(self.chooseSwitchin())
