from utilities import Dp, choose, to_list
from output import Op
from character import PlayerCharacter, EnemyCharacter, AbstractCharacter
from item import Item
from serialize import AbstractJsonSerialable
import os

PLAYER_TEAM_DIRECTORY = 'users'

"""
Teams are used to group characters
together so that the program knows
who are enemies, and who are allies.
"""
class AbstractTeam(AbstractJsonSerialable):
    def __init__(self, type: str, name: str, members=[]):
        super(AbstractTeam, self).__init__(type=type)
        self.name = name
        self.members = []
        for member in members:
            self.addMember(member)
        self.enemy = None
        self.addSerializedAttributes(
            "name",
            "members"
        )

    """
    Reads a json file, then returns the team contained in that file
    """
    @staticmethod
    def loadTeam(path: str) -> 'AbstractTeam':
        ret = None
        dict = AbstractJsonSerialable.readFile(path)
        if dict["type"] == "PlayerTeam":
            character = AbstractCharacter.loadJson(dict["members"][0])
            ret = PlayerTeam(dict["name"], character)
            for item in dict.get('inventory', []):
                ret.obtain(Item.read_json(item))
        elif dict["type"] == "EnemyTeam":
            ret = EnemyTeam([member['name'] for member in dict["members"]], dict["members"][0].level)
        else:
            raise Error('Type not found: ' + dict["type"])

        return ret

    def addMember(self, member: 'AbstractCharacter'):
        """
        Adds a character to this' team, if they are not
        already on the team
        """
        if member not in self.members:
            self.members.append(member)
            member.team = self

    # balance this later
    def getXpGiven(self):
        """
        How much xp will be given
        once this team is
        defeated.
        """
        xp = 0
        for member in self.members:
            xp += member.level * 10
        return xp / len(self.members)

    def updateMembersRem(self):
        newMembersRem = []
        for member in self.members_rem:
            if not member.isKoed():
                newMembersRem.append(member)
                member.update()
            else:
                Op.add(member.name + " is out of the game!")
                Op.display()
        self.members_rem = newMembersRem

    def is_up(self):
        """
        Use to see if your team still exists
        """

        return len(self.members_rem) != 0

    def one_left(self):
        """
        Detects when you have only one member left
        """
        return len(self.members_rem) == 1

    def initialize(self):
        """
        Ready the troops!
        """
        # I will definitely want to add a forEach sort of method
        self.members_rem = []
        for member in self.members:
            member.initForBattle()
            self.members_rem.append(member)
        self.active = self.members_rem[0]

    def displayData(self):
        """
        Show info for a team
        """
        Op.add(self.name)
        for member in self.members_rem:
            Op.add("* " + member.name + " " + str(int(member.remHp)) + "/" + str(int(member.maxHp)))
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
        self.active.choose_attack()

    def shouldSwitch(self) -> bool:
        """
        Returns whether or not this team
        should change who is active
        """
        raise NotImplementedError('Team method shouldSwitch is abstract')

    def chooseSwitchin(self) -> 'AbstractCharacter':
        """
        This is abstract: each subclass should implement it
        """
        raise NotImplementedError('Team method chooseSwitchin is abstract')



class PlayerTeam(AbstractTeam):
    def __init__(self, name, member):
        super(PlayerTeam, self).__init__("PlayerTeam", name, [member])
        self.inventory = []
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
        for member in self.members_rem:
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

    def save(self):
        self.writeToFile(os.path.join(PLAYER_TEAM_DIRECTORY, self.name.replace(" ", "_").lower() + ".json"))


class EnemyTeam(AbstractTeam):
    def __init__(self, member_names: list, level: int):
        super(self.__class__, self).__init__("EnemyTeam", "Enemy Team")
        member_names = to_list(member_names)
        for name in member_names:
            member = EnemyCharacter.load_enemy(name)
            member.level = level
            self.addMember(member)

    """
    AI stuff
    BENCHIT NEEDS FIX
    general improvements needed
    """
    def shouldSwitch(self):
        """
        First, check if our active can KO
        """
        if self.one_left() or self.enemy.active.calcDmgTaken(self.active, self.active.best_attack()) >= self.enemy.active.remHp:
            return False


        """
        Second, check if an ally can KO
        """
        for member in self.members_rem:
            if self.enemy.active.calcDmgTaken(member, member.best_attack()) * 0.75 >= self.enemy.active.remHp:
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
        for member in self.members_rem:
            if self.enemy.active.calcDmgTaken(member, member.best_attack()) * 0.75 >= self.enemy.active.remHp:
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
            array = self.members_rem
        else:
            array = can_ko

        rand = random.randint(0, len(array) - 1)
        return array[rand]
