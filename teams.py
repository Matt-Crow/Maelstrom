from utilities import *
from characters import *

"""
Teams
"""
class AbstractTeam(object):
    """
    Teams are used to group characters
    together so that the program knows
    who are enemies, and who are allies.
    """
    # balance this later
    def xp_given(self):
        """
        How much xp will be given
        once this team is
        defeated.
        """
        xp = 0
        for member in self.team:
            xp += member.level * 10
        return xp / len(self.team)
    
    def update_members_rem(self):
        new_members_rem = []
        for member in self.members_rem:
            if not member.check_if_KOed():
                new_members_rem.append(member)
                member.update()
            else:
                Op.add(member.name + " is out of the game!")
                Op.dp()
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
            
    def switch(self, member):
        """
        You're up!
        """
        self.active = member
    
    def initialize(self):
        """
        Ready the troops!
        """
        self.members_rem = []
        for member in self.team:
            member.init_for_battle()
            self.members_rem.append(member)
        self.active = self.members_rem[0]
    
    def list_members(self):
        """
        Display the data
        of each member
        of the team
        """
        Op.add(self.name)
        Op.dp()
        for member in self.team:
            member.display_data()
    
    def display_data(self):
        """
        Show info for a team
        """
        Op.add(self.name)
        for member in self.members_rem:
            Op.add("* " + member.name + " " + str(int(member.HP_rem)) + "/" + str(int(member.get_stat("HP"))))
        Op.add("Currently active: " + self.active.name)
        self.active.display_mutable_stats()
        Op.add(self.active.name + "'s Energy: " + str(self.active.energy))
        Op.add("Active enemy: " + self.enemy.active.name + " " + str(int(self.enemy.active.HP_rem)) + "/" + str(int(self.enemy.active.get_stat("HP"))))
        Op.dp()
    
    def __str__(self):
        return self.name
       
    def do_turn(self):
        """
        This is where stuff happens
        """
        if self.active.check_if_KOed():
            self.choose_switchin()
        self.switched_in = False
        self.choose_action()
        pause()

class PlayerTeam(AbstractTeam):
    def __init__(self, name, member):
        self.team = []
        self.name = name
        self.team.append(PlayerCharacter(member["name"], member["data"], member["level"]))
        self.inventory = []
        for member in self.team:
            member.team = self
    
    """
    Choices are made using these functions
    """                 
    def choose_switchin(self):
        """
        Who will fight?
        """
        choices = []
        for member in self.members_rem:
            if member != self.active:
                choices.append(member)
        
        self.switch(choose("Who do you want to bring in?", choices))
            
        Op.add(self.active.name + " up!")
        Op.dp()
                                                                        
    def choose_action(self):
        """
        What to do, what to do...
        """
        self.display_data()
        choices = ["Attack"]
        
        if not self.one_left():
            choices.append("Switch")
        
        if choose("What do you wish to do?", choices) == "Switch":
            self.choose_switchin()
            self.switched_in = True
        self.active.choose_attack()
    
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
    
    def customize(self):
        self.team[0].customize()
    
class EnemyTeam(AbstractTeam):
    def __init__(self, members, level):
        self.team = []
        self.name = "Enemy team"
        
        members = to_list(members)
        for new_member in members:
            self.team.append(EnemyCharacter(new_member, level))
        for member in self.team:
            member.team = self
    
    """
    AI stuff
    BENCHIT NEEDS FIX
    general improvements needed
    """
    def should_switch(self):
        """
        First, check if our active can KO
        """
        if self.one_left():
            return "Attack"
        if self.enemy.active.calc_DMG(self.active, self.active.best_attack()) >= self.enemy.active.HP_rem:
            return "Attack"
        """
        Second, check if an ally can KO 
        """
        for member in self.members_rem:
            if self.enemy.active.calc_DMG(member, member.best_attack()) * 0.75 >= self.enemy.active.HP_rem:
                return "Switch"
        
        # Default
        return "Attack"
        
    # comment     
    def who_switch(self):
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

    """
    Choices are made using these functions
    """                 
    def choose_switchin(self):
        """
        Who will fight?
        """
        self.switch(self.who_switch())
            
        Op.add(self.active.name + " up!")
        Op.dp()
                                                                        
    def choose_action(self):
        """
        What to do, what to do...
        """
        self.display_data()
        
        choices = ["Attack"]
        
        if not self.one_left():
            choices.append("Switch")
            
        if self.should_switch() == "Switch":
            self.choose_switchin()
            self.switched_in = True
        self.active.choose_attack()
