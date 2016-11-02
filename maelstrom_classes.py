"""
Started October 28, 2015
28/10/2015-: Built Attack, Warrior (later renamed Character), and Team
Week 2: Revised/improved/reordered functions
23/11/2015 - 27/11/2015: Implemented Battle
30/11/2015 - 4/12/2015: Finished most of PvP
7/12/2015 - 11/12/2015: Implemented Weather, redid stat boosts 
14/12/2015 - 18/12/2015: Added data files
31/12/2015 - 1/1/2016: Worked on Special file reading

18/10/2016 - 22/10/2016: General cleanup/improvement

Version 0.6
"""

import random


# does not work

#from Maelstrom import debug, do_MHC
do_MHC = True
debug = True

"""
Attack: 
Character:
Team:
Weather: 
Battle: 
"""

"""
To do:

Add abilities
Add items
add AI

add cancel option

bug: debug shows active enemy alongside team while checking boosts
bug: extra turn if second team wins
"""

def mod(num):
    """
    A useful little guy
    """
    if num < 1:
        num = 1
    return num

def choose(question, options):
    
    if len(options) == 1:
        return options[0]
    
    print question
    
    num = 1
    for option in options:
        try:
            name = option.name  
        except:
            name = option
        
        print num, ":", name    
        num += 1
    
    answered = False
    
    while not answered:
        choice = raw_input(" ")
        for option in options:
            try:
                compare = option.name.lower()
            except:
                compare = option.lower()
            if choice.lower() == compare:
                    return option
            elif choice == str(options.index(option) + 1):
                return option
        else:
            print "That isn't an option..."

# balance chances later
class Attack:
    """
    The regular attacks all characters can use
    as well as characters' exclusive Specials
    """
    def __init__(self, (name, damage_multiplier, chances, mhc_mults, target, side_effect)):
        """
        Copy-paste: 
        (name, damage_multiplier, (miss%, crit%), (miss*, crit*), (ally_or_enemy, act_any_all), (eff, eff_LV, eff_dur))  
        """
        self.name = name.replace("_", " ")
        self.mult = float(damage_multiplier)
        self.miss = int(chances[0])
        self.crit = int(chances[1])
        self.miss_mult = float(mhc_mults[0])
        self.crit_mult = float(mhc_mults[1])
        self.ally_or_enemy = target[0]
        self.act_any_all = target[1]
        self.eff = int(side_effect[0])
        self.eff_LV = int(side_effect[1])
        self.eff_dur = int(side_effect[2])
        
    def get_mult(self):
        """
        The attack's multiplier
        """
        return self.mult
        
    def get_miss(self):
        """
        Did the attack miss?
        """
        return self.miss
        
    def get_crit(self):
        """
        Did it score a critical hit?
        """
        return self.crit
        
    def calc_MHC(self):
        """
        Used to calculate hit type
        """
        rand = random.randint(1, 100)
        if debug:
            print "rand in calc_MHC: ", rand
            print "Crit:", 100 - self.get_crit()
            print "Miss:", self.get_miss()
            
        if rand <= self.get_miss():
            print "A glancing blow!"
            return self.miss_mult
            
        elif rand >= 100 - self.get_crit():
            print "A critical hit!"
            return self.crit_mult
            
        else: 
            return 1.0

    # make choose() used here, once it is implemented
    def use(self, user):
        """
        Use your attack
        """
        
        if self.ally_or_enemy == "ally":
            target_team = user.team
               
        elif self.ally_or_enemy == "enemy":
            target_team = user.team.enemy
        
        targets = []
        
        if self.act_any_all == "act":
            targets.append(target_team.active)
            
        elif self.act_any_all == "all":
            for member in target_team.members_rem:
                targets.append(member)
                
        elif self.act_any_all == "any":
            hit = choose("Who do you wish to hit?", target_team.members_rem)
            targets.append(hit)
                        
        for warrior in targets:               
            warrior.take_DMG(user, self)
            if self.eff != 0:
                warrior.boost(self.eff, self.eff_LV, self.eff_dur)

class Element:
    def __init__(self, name, weakness):
        self.name = name
        self.weakness = weakness

class Character:
    """
    A Class containing all the info for a character
    """
        
    """
    Initializers:
        Used to 'build' the characters
    """

    def __init__(self, data):
        """
        base stats: (def ratio, res ratio, con ratio)
        """
        self.name = data[0]
        self.base_stats = data[1]
        self.element = data[2]
        self.special = data[3]
        self.level = 1
        self.XP = 0
        self.level_set = 1
       
    def calc_stats(self):
        """
        Calculate a character's stats
        """
        TOTAL = (self.level + 5) * 0.04 * 1000
        
        DEFRAT = 0.7 + self.base_stats[0] * 0.025
        OFFRAT = 1.0 - DEFRAT
        DEF = DEFRAT * TOTAL
        OFF = OFFRAT * TOTAL
        
        HPRAT = 0.71
        self.max_HP = HPRAT * DEF
        DEF -= self.max_HP
        
        RESRAT = 0.5 + self.base_stats[1] * 0.05
        ARMRAT = 1.0 - RESRAT
        
        self.res = RESRAT * DEF
        self.arm = ARMRAT * DEF
        
        DMGRAT = 0.33
        self.dmg = DMGRAT * OFF
        OFF -= self.dmg
        
        CONRAT = 0.5 + self.base_stats[2] * 0.05
        STRRAT = 1.0 - CONRAT
        self.con = CONRAT * OFF
        self.str = STRRAT * OFF
    
    def reset_HP(self):
        """
        Restore HP back to full
        """
        self.HP_rem = self.get_HP()
    
    def reset_boosts(self):
        """
        Set your 
        boosts 
        as a list
        """
        self.boosts = []
    
    def init_for_battle(self):
        """
        Prepare for battle!
        """
        self.reset_HP()
        self.reset_boosts()

    """
    Data obtaining functions:
        Used to get data about a character
    """
        
    def get_HP(self):
        return int(self.max_HP)
    
    def get_dmg(self):
        return mod(self.dmg)
    
    def get_arm(self):
        return mod(self.arm * self.get_boost("ARM"))
        
    def get_str(self):
        return mod(self.str * self.get_boost("STR"))
        
    def get_con(self):
        return mod(self.con * self.get_boost("CON"))
    
    def get_res(self):
        return mod(self.res * self.get_boost("RES"))
    
    def display_data(self):
        """
        Print info on a character
        """
        self.calc_stats()
        print "----------"
        print "Lv.", self.level, self.name
        print self.element.name
        print " " 
        print "HP", self.HP_rem, "/", self.get_HP()
        print "DMG", int(self.get_dmg())
        print "STR", int(self.get_str())
        print "ARM", int(self.get_arm())
        print "CON", int(self.get_con())
        print "RES", int(self.get_res())
        print " "
        if self.special != "None":
            print self.special.name
        print self.XP, "/", self.level * 10
        print "----------"

    """
    Battle functions:
        Used during battle
    """
   
    def boost(self, stat, amount, duration):
        """
        Increase or lower stats in battle
        """
        
        self.boosts.append([stat, amount, duration])
    
    def get_boost(self, stat):
        """
        Returns stat boost
        """
        ret = 1
        for boost in self.boosts:
            if boost[0] == stat:
                ret += boost[1]
        return ret
        
    def update_boosts(self):
        new_boosts = []
        for boost in self.boosts:
            if boost[2] != 0:
                boost[2] -= 1
                new_boosts.append(boost)
        self.boosts = new_boosts
        if debug:
            print self.name, "'s boosts:", self.boosts
        
    def heal(self, percent):
        """
        Restores HP.
        Converts an INTEGER
        to a percentage.
        """
        healing = self.get_HP() * (float(percent) / 100)
        self.HP_rem = int(self.HP_rem + healing)
        if debug:
            print self.name, "healed", healing, "HP"
            
        if self.HP_rem > self.get_HP():
            self.HP_rem = self.get_HP()
    
    def check_effectiveness(self, attacker):
        """
        Used to calculate elemental damage taken
        """
        if self.element.weakness == attacker.element.name:
            return 1.5
        elif attacker.element.weakness == self.element.name:
            return 0.67
        else:
            return 1.0
    # effectiveness
    def calc_DMG(self, attacker, attack_used):
        
        phys_damage = attacker.get_str() / self.get_arm()
        
        ele_damage = attacker.get_con() / self.get_res()
        
        damage = (phys_damage + ele_damage) / 2 * attack_used.get_mult() * attacker.get_dmg()
        
        if attacker.team.switched_in:
            damage = damage * 0.75
        
        if do_MHC:
            damage = damage * attack_used.calc_MHC()
            
        if debug:
            print "Physical Mult:", phys_damage
            print "Elemental Mult:", ele_damage
            print "Raw damage:", (phys_damage + ele_damage) / 2
            print "Damage:", damage
            
        return int(damage)
 
    def take_DMG(self, attacker, attack_used):
        self.HP_rem = int(self.HP_rem - self.calc_DMG(attacker, attack_used))
        
    def check_if_KOed(self):
        """
        Am I dead yet?
        """
        return self.HP_rem <= 0
    
    """
    Post-battle actions:
        Occur after battle
    """        
    def gain_XP(self, amount):
        """
        Give experience.
        Caps at the most XP required for a battle
        (Can't level up twice after one battle)
        """
        self.XP = self.XP + amount
        if self.XP > self.level * 10: 
            if self.can_level_up():
                print self.name, "leveled up!"
                self.level_up()
            else:
                print self.name, "is being held back... perhaps a special item will help?"
    
    def level_up(self):
        """
        Increases level
        """
        self.XP = 0
        self.level += 1
        self.calc_stats()
        self.reset_HP()
        self.display_data()
    
    def can_level_up(self):
        """
        Make sure you are not blocked by your current level cap
        """
        return self.level < self.level_set * 5
        
    def plus_level_set(self):
        """
        Increases your 
        level cap by 5
        """
        self.level_set = self.level_set + 1

class Team:
    """
    Teams are used to group characters
    together so that the program knows
    who are enemies, and who are allies.
    """
    def __init__(self, name, members, single = False):
        self.team = []
        self.name = name
        
        if single:
            self.team.append(Character(members))
        else:
            for new_member in members:
                self.team.append(Character(new_member))
        
    def add_member(self, new_member):
        """
        Add a member to a team.
        """
        for member in self.team:
            if new_member[0] == member.name:
                return False
        self.team.append(Warrior(new_member))
        
    def apply_team(self):
        """
        Let all members
        know what team
        they are on
        """
        for member in self.team:
            member.team = self
    
    def find_enemy(self, teams):
        """
        Take a list of teams 
        (from Battle), and
        return the one that 
        is not self.
        """
        for team in teams:
            if team != self:
                return team
    
    # balance this later
    def xp_given(self):
        """
        How much xp will be given
        once this team is
        defeated.
        """
        xp = 0
        for member in self.use:
            xp += member.level * 10
        return xp / len(self.use)
    
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
       
    def knock_out(self, member):
        """
        Delete a warrior
        from members_rem
        """
        self.members_rem.remove(member)
    
    def init_energy(self):
        """
        Set your energy to 0.
        """
        self.energy = 0
    
    def gain_energy(self, amount = 1):
        """
        Increase your energy.
        Default is 1.
        """
        self.energy = self.energy + amount
        
        if self.energy > 7:
            self.energy = 7
        
    def lose_energy(self, amount):
        """
        Decrease your energy
        """
        self.energy = self.energy - amount
        if self.energy < 0:
            self.energy = 0
        
    def init_active(self):
        """
        Elect a leader
        """
        self.active = self.members_rem[0]
        
    def switch(self, member):
        """
        You're up!
        """
        self.active = member
          
    def show_team(self, exclude_active = False):
        """
        Print the names of all team members
        """
        print " "
        for member in self.members_rem:
            if exclude_active:
                if member != self.active:
                    print "*", member.name
            else:
                print "*", member.name
        print " "
    
    def initialize(self):
        """
        Ready the troops!
        """
        self.init_energy()
        self.apply_team()
        self.members_rem = []
        for member in self.team:
            member.calc_stats()
            member.init_for_battle()
            self.members_rem.append(member)
        self.init_active()
    
    def display_data(self):
        """
        Show info for a team
        """
        print " "
        print self.name
        for member in self.team:
            print " "
            member.display_data()
        print " "
    
    """
    Choices are made using these functions
    """    
    def choose_attack(self):
        """
        How doth thee strike?
        """
        
        attack_options = []
        
        # to avoid editting attacks...
        for attack in attacks:
            attack_options.append(attack)
        
        if self.energy >= 2 and self.active.special != "None":
            attack_options.append(self.active.special) 
        
        choice = choose("What attack do you wish to use?", attack_options)
        
        if choice == self.active.special:
            self.lose_energy(2)
        
        choice.use(self.active)
              
    def choose_switchin(self):
        """
        Who will fight?
        """
        
        if self.one_left():
            self.switch(self.members_rem[0])
            return
        
        choices = []
        for member in self.members_rem:
            if member != self.active:
                choices.append(member)
        
        switch_for = choose("Who do you want to bring in?", choices)
        
        self.switch(switch_for)
          
        print self.active.name, "up!"
                                        
    def choose_action(self):
        """
        What to do, what to do...
        """
        
        for member in self.members_rem:
            print member.name, member.HP_rem, "/", member.get_HP(), member.element.name
            
        print "Currently active:", self.active.name
        print "Energy:", self.energy
        
        print "Active enemy:", self.enemy.active.HP_rem, "/", self.enemy.active.get_HP(), self.enemy.active.element.name
        
        choices = ["Attack"]
        
        if (not self.one_left()) and self.energy >= 1:
            choices.append("Switch")
        
        attack_switch = choose("What do you wish to do?", choices)
        
        if attack_switch == "Switch":
            self.choose_switchin()
            self.lose_energy(1)
            self.switched_in = True
        self.choose_attack()
        
    def do_turn(self):
        """
        This is where stuff happens
        """
        new_members_rem = []
        for member in self.members_rem:
            if not member.check_if_KOed():
                new_members_rem.append(member)
            else:
                print member.name, "is out of the game!"
        self.members_rem = new_members_rem
        
        if self.active.check_if_KOed() and self.is_up():
            self.choose_switchin()
        
        if self.is_up():
            self.switched_in = False
            self.gain_energy()
            
            for member in self.members_rem:
                member.update_boosts()
                
            self.choose_action()

class Weather:
    """
    This is what makes Maelstrom unique!
    Weather provides in-battle effects
    that alter the stats of characters
    """
    def __init__(self, type, intensity, msg):
        """
        The type determines what sort of effect will
        be applied to all participants in a battle.
        The intensity is how potent the effect will be.
        The msg is what text will show to help
        the player determine the weather.
        """
        self.type = type
        self.intensity = intensity
        self.msg = msg
        
    def do_effect(self, affected):
        """
        Apply stat changes 
        to a team
        """
        
        if self.type == "Lightning":
            for person in affected:
                person.boost("CON", self.intensity/100, 1)
            
        if self.type == "Wind":
            for person in affected:
                person.boost("STR", self.intensity/100, 1)
            
        if self.type == "Hail":
            for person in affected:
                person.heal(-self.intensity)
        
        if self.type == "Rain":
            for person in affected:
                person.heal(self.intensity)
                
    def disp_msg(self):
        """
        Print a message showing
        the weather condition
        """
        print self.msg

class Battle:
    """
    The Battle class pits 2 teams
    against eachother, 
    initializing them
    and the weather.
    """
    def __init__(self, team_size, weather_list):
        """
        Maximum team size,
        Weather should be improved
        """
        self.teams = []
        self.team_size = team_size
        self.forecast = weather_list
        
    def load_team(self, team):
        """
        Add a team 
        to the battle
        """
        self.teams.append(team)
        
        # add choose later
        if len(team.team) > self.team_size:
            print "Select which", self.team_size, "members you wish to use"
            for member in team.team:
                print "*", member.name
            
            choose = self.team_size
            team.use = []
            
            while choose > 0:
                add = raw_input("")
                for member in team.team:
                    if add.lower() == member.name.lower() and member not in team.use:
                        team.use.append(member)
                        choose = choose - 1
        else:
            team.use = team.team
    
    def check_winner(self):
        """
        Runs when one
        teams loses all
        members.
        """
        for team in self.teams:
            if team.is_up():
                winner = team
        print winner.name, "won!"
    
    def begin(self):
        """
        Prepare both teams
        for the match.
        """
        for team in self.teams:
            team.initialize()
            team.enemy = team.find_enemy(self.teams)
            print " "
            print " "
            print " "
            print team.name
            
            for member in team.team:
                if member not in team.use:
                    team.knock_out(member)
                else:
                    member.display_data()
            team.init_active()
        try:
            num = random.randrange(0, len(self.forecast) - 1)
        except:
            if debug:
                print "Only one weather option"
            num = 0
        self.weather = self.forecast[num]
        self.weather.disp_msg()
    
    def end(self):
        """
        The stuff that takes place after battle
        """
        for team in self.teams:
            for member in team.use:
                xp = team.enemy.xp_given()
                member.gain_XP(xp)
                    
    def play(self):
        """
        Used to start
        the battle
        """
        self.begin()
        while self.teams[0].is_up() and self.teams[1].is_up():
            for team in self.teams:
                if team.is_up():
                    self.weather.do_effect(team.members_rem)
                    team.do_turn()
                    
        self.check_winner()
        self.end()

no_MHC = (0, -1)
no_MHC_mult = (1, 1)
no_eff = (0, 0, 0)
act_ene = ("enemy", "act")
        
slash = Attack(("slash", 1.0, (20, 20), (0.75, 1.25), act_ene, no_eff))
jab = Attack(("jab", 0.85, (15, 40), (0.8, 1.88), act_ene, no_eff))
slam = Attack(("slam", 1.3, (30, 10), (0.69, 1.2), act_ene, no_eff))

attacks = (slash, jab, slam)

print "Oops! You ran the wrong file!"
print "Try running Maelstrom.py instead."