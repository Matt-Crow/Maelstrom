from utilities import Dp, choose, to_list
from output import Op
from character import PlayerCharacter, EnemyCharacter

"""
Teams
"""
class AbstractTeam(object):
    """
    Teams are used to group characters
    together so that the program knows
    who are enemies, and who are allies.
    """
    
    def __init__(self, name: str, members=[]):
        """
        Members is a list of AbstractCharacters
        """
        self.name = name
        self.members = []
        for member in members:
            self.add_member(member)
        
        
    def add_member(self, member: 'AbstractCharacter'):
        """
        Adds a character to this' team, if they are not
        already on the team
        """
        if member not in self.members:
            self.members.append(member)
            member.team = self
        
        
    # balance this later
    def xp_given(self):
        """
        How much xp will be given
        once this team is
        defeated.
        """
        xp = 0
        for member in self.members:
            xp += member.level * 10
        return xp / len(self.members)


    def update_members_rem(self):
        new_members_rem = []
        for member in self.members_rem:
            if not member.check_if_KOed():
                new_members_rem.append(member)
                member.update()
            else:
                Op.add(member.name + " is out of the game!")
                Op.display()
        self.members_rem = new_members_rem


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
        self.members_rem = []
        for member in self.members:
            member.init_for_battle()
            self.members_rem.append(member)
        self.active = self.members_rem[0]
        

    def display_data(self):
        """
        Show info for a team
        """
        Op.add(self.name)
        for member in self.members_rem:
            Op.add("* " + member.name + " " + str(int(member.HP_rem)) + "/" + str(int(member.max_hp)))
        Op.add("Currently active: " + self.active.name)
        Op.add(self.active.get_data())
        Op.add(self.active.name + "'s Energy: " + str(self.active.energy))
        Op.add("Active enemy: " + self.enemy.active.name + " " + str(int(self.enemy.active.HP_rem)) + "/" + str(int(self.enemy.active.max_hp)))
        Op.display()


    def __str__(self):
        return self.name


    def do_turn(self):
        """
        This is where stuff happens
        """
        if self.active.check_if_KOed():
            self.active = self.choose_switchin()
        self.switched_in = False
        
        self.display_data()
        if self.should_switch():
            self.active = self.choose_switchin()
            self.switched_in = True
        self.active.choose_attack()
    
    
    
    def should_switch(self) -> bool:
        """
        Returns whether or not this team
        should change who is active
        """
        raise NotImplementedError('Team method should_switch is abstract')
        
        
    def choose_switchin(self) -> 'AbstractCharacter':
        """
        This is abstract: each subclass should implement it
        """
        raise NotImplementedError('Team method choose_switchin is abstract')
        


class PlayerTeam(AbstractTeam):
    def __init__(self, name, member):
        super(self.__class__, self).__init__(name, [member])
        self.inventory = []
    
    

    """
    Choices are made using these functions
    """
    def should_switch(self) -> bool:
        """
        Asks the user if they want to
        switch before attacking
        """
        self.display_data()
        
        return len(self.members) > 1 and choose('Do you want to switch your active character?', ['Yes', 'No']) == 'Yes' 
    
    
    def choose_switchin(self):
        """
        Who will fight?
        """
        choices = []
        for member in self.members_rem:
            if member != self.active:
                choices.append(member)
        self.display_data()
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
            member.display_data()
            options.append(member)

        options.reverse()
        managing = choose("Who do you wish to manage?", options)
        
        if managing is not "Exit":
            managing.manage()




class EnemyTeam(AbstractTeam):
    def __init__(self, member_names: list, level: int):
        super(self.__class__, self).__init__('Enemy Team')

        member_names = to_list(member_names)
        for name in member_names:
            member = EnemyCharacter.load_enemy(name)
            member.level = level
            self.add_member(member)
            
            

    """
    AI stuff
    BENCHIT NEEDS FIX
    general improvements needed
    """
    def should_switch(self):
        """
        First, check if our active can KO
        """
        if self.one_left() or self.enemy.active.calc_DMG(self.active, self.active.best_attack()) >= self.enemy.active.HP_rem:
            return False
        
        
        """
        Second, check if an ally can KO
        """
        for member in self.members_rem:
            if self.enemy.active.calc_DMG(member, member.best_attack()) * 0.75 >= self.enemy.active.HP_rem:
                return True

        
        # Default
        return False


    # comment
    def choose_switchin(self):
        """
        Used to help the AI
        decide who to switch in
        """

        """
        Can anyone KO?
        """
        can_ko = []
        for member in self.members_rem:
            if self.enemy.active.calc_DMG(member, member.best_attack()) * 0.75 >= self.enemy.active.HP_rem:
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
