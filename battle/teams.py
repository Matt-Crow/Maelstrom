from utilities import Dp, choose, to_list
from output import Op
from character import PlayerCharacter, EnemyCharacter, AbstractCharacter
from item import Item
from serialize import AbstractJsonSerialable
import os
import random

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
            ret = PlayerTeam(**jdict)
        elif type =="EnemyTeam":
            jdict["members"] = [AbstractCharacter.deserializeJson(member) for member in jdict["members"]]
            ret = EnemyTeam(**jdict)
        else:
            raise Error("Type not found for AbstractTeam: {0}".format(type))
        return ret

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

    def updateMembersRem(self):
        newMembersRem = []
        for member in self.membersRem:
            if not member.isKoed():
                newMembersRem.append(member)
                member.update()
            else:
                Op.add(member.name + " is out of the game!")
                Op.display()
        self.membersRem = newMembersRem

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

    """
    Show info for a team
    """
    def displayData(self):
        Op.add(self.name)
        for member in self.membersRem:
            Op.add("* " + member.name + " " + str(int(member.remHp)) + "/" + str(int(member.maxHp)))
        if hasattr(self, "active"):
            Op.add("Currently active: " + self.active.name)
            Op.add(self.active.getDisplayData())
            Op.add(self.active.name + "'s Energy: " + str(self.active.energy))
        if self.enemy:
            Op.add("Active enemy: " + self.enemy.active.name + " " + str(int(self.enemy.active.remHp)) + "/" + str(int(self.enemy.active.maxHp)))
        Op.display()

    def __str__(self):
        return self.name

    def doTurn(self):
        """
        This is where stuff happens
        """
        if self.active.isKoed():
            self.active = self.chooseSwitchin()
        self.switched_in = False

        self.displayData()
        if self.shouldSwitch():
            self.active = self.chooseSwitchin()
            self.switched_in = True
        self.active.chooseActive()

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

    """
    Choices are made using these functions
    """
    def shouldSwitch(self) -> bool:
        """
        Asks the user if they want to
        switch before attacking
        """
        self.displayData()

        return len(self.members) > 1 and choose('Do you want to switch your active character?', ['Yes', 'No']) == 'Yes'

    def chooseSwitchin(self):
        """
        Who will fight?
        """
        choices = []
        for member in self.membersRem:
            if member != self.active:
                choices.append(member)
        self.displayData()
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

    def manage(self):
        """
        Displays the team management menu
        """
        options = ["Exit"]
        for member in self.members:
            member.displayData()
            options.append(member)

        options.reverse()
        managing = choose("Who do you wish to manage?", options)

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

        for member in can_ko:
            Dp.add(member.name)

        Dp.add("can KO")
        Dp.dp()

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
