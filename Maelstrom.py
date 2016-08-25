"""
Started October 28, 2015
28/10/2015-: Built Attack, Warrior, and Team
Week 2: Revised/improved/reordered functions
Week 2: Revised/improved/reordered functions
23/11/2015 - 27/11/2015: Implemented Battle
30/11/2015 - 4/12/2015: Finished most of PvP
7/12/2015 - 11/12/2015: Implemented Weather, redid stat boosts 
14/12/2015 - 18/12/2015: Added data files
31/12/2015 - 1/1/2016: Worked on Special file reading

Version 0.6
Currently working on files
"""

import random

specials = open("mael_specials.txt")
characters = open("mael_characters.txt")
weather = open("mael_weather.txt")

"""
Attack: [DONE]
Warrior:
Team:
Weather: 
Battle:
"""

"""
To do:

Add abilities
Add items
add AI

add other files for specials and characters

add cancel option

redo calc_stats?

add key commands

bug: debug shows active enemy alongside team while checking boosts
bug: extra turn if second team wins

TIP: You can use "s" instead of your special's name to use it
"""

do_MHC = True
debug = False

boarder = {"top": "^==^==^==^==^", "bottom": "V==V==V==V==V", "break": " "}

def mod(num):
    """
    A useful little guy
    """
    if num < 1:
        num = 1
    return num

weaknesses = {"Lightning": "Wind", "Wind": "Hail", "Hail": "Rain", "Rain": "Lightning"}

class Attack:
    """
    The regular attacks all characters can use
    as well as characters' exclusive Specials
    """
    
    def __init__(self, (name, damage_multiplier, chances, target, side_effect)):
        self.name = name.replace("_", " ")
        self.mult = float(damage_multiplier)
        self.miss = int(chances[0])
        self.crit = int(chances[1])
        self.ally_or_enemy = target[0]
        self.act_any_all = target[1]
        self.eff = int(side_effect[0])
        self.eff_LV = int(side_effect[1])
        
    def get_mult(self):
        return self.mult
        
    def get_miss(self):
        return self.miss
        
    def get_crit(self):
        return self.crit
        
    def calc_MHC(self):
        """
        Used to calculate hit type
        """
        rand = random.randrange(1, 8)
        if debug:
            print "rand in calc_MHC: ", rand
            
        if rand <= self.get_miss():
            print "A glancing blow!"
            return 0.75
            
        elif rand >= self.get_crit():
            print "A critical hit!"
            return 1.25
            
        else: 
            return 1.0

    def use(self, user):
        """
        Use your attack
        """
        
        if self.ally_or_enemy == "ally":
            target_team = user.team
               
        elif self.ally_or_enemy == "enemy":
            target_team = user.team.enemy
        
        if self.act_any_all == "any":
            print "Who do you wish to hit?"
            target_team.show_team()
            decided = False
            while not decided:
                choice = raw_input(" ")
                for member in target_team.members_rem:
                    if member.name.lower() == choice.lower():
                        decided = True
                        member.take_DMG(user, self)
                        member.inflict(self.eff, self.eff_LV)
            
        elif self.act_any_all == "all":
            for member in target_team.members_rem:
                member.take_DMG(user, self)
                member.inflict(self.eff, self.eff_LV)    
            
        elif self.act_any_all == "act":
            target = target_team.active
            target.take_DMG(user, self)
            target.inflict(self.eff, self.eff_LV)



class Warrior:
    """
    A Class containing all the info for a character
    """
        
    """
    Initializers:
        Used to 'build' the characters
    """

    def __init__(self, data):
        """
        base stats: (def ratio, HP ratio, ele ratio)
        """
        self.name = data[0]
        self.base_stats = data[1]
        self.element = data[2]
        
        special_found = False
        
        for special in special_list.keys():
            if data[3] == special:
                self.special = Attack(special_list[special])
                special_found = True
        if not special_found:
            self.special = "None"
        
        #self.special = data[3]
        self.level = 1
        self.XP = 0
        self.level_set = 1
        
    def calc_stats(self):
        """
        Calculate a character's stats
        """
        TOTAL = (self.level + 5) * 0.04 * 1000
        DEFRAT = 0.715 + self.base_stats[0] * 0.035
        OFFRAT = 1.0 - DEFRAT
        DEF = DEFRAT * TOTAL
        OFF = OFFRAT * TOTAL
        
        HPRAT = 0.875 + self.base_stats[1] * 0.03
        ARMRAT = 1.0 - HPRAT
        
        HP = DEF * HPRAT
        ARM = DEF * ARMRAT
        
        ELERAT = 0.5 + self.base_stats[2] * 0.05
        STRRAT = 1.0 - ELERAT
        
        STR = OFF * STRRAT
        ELE = OFF * ELERAT
        
        self.HP = HP
        self.arm = ARM
        self.str = STR
        self.ele = ELE
        
    def reset_HP(self):
        self.HP_rem = self.get_HP()
    
    def reset_boosts(self):
        self.boosts = [0, 0, 0]
    
    def init_for_battle(self):
        self.reset_HP()
        self.reset_boosts()

    """
    Data obtaining functions:
        Used to get data about a character
    """
        
    def get_HP(self):
        self.calc_stats()
        return int(self.HP)
    
    # these three are kinda messy    
    def get_arm(self):
        self.calc_stats()
        return mod(int(self.arm * (1 + self.boosts[0] * 0.05)))
        
    def get_str(self):
        self.calc_stats()
        return mod(int(self.str * (1 + self.boosts[1] * 0.05)))
        
    def get_ele(self):
        self.calc_stats()
        return mod(int(self.ele * (1 + self.boosts[2] * 0.05)))
        
    def check_ele(self):
        return self.element

    def display_data(self):
        """
        Print info on a character
        """
        self.calc_stats()
        print "----------"
        print "Lv.", self.level, self.name
        print self.check_ele()
        print " " 
        print "HP", self.HP_rem, "/", self.get_HP()
        print "Str", self.get_str()
        print "Arm", self.get_arm()
        print "Ele", self.get_ele()
        print " "
        if self.special != "None":
            print self.special.name
        print self.XP, "/", self.level * 10
        print "----------"

    """
    Battle functions:
        Used during battle
    """
   
    def inflict(self, stat, level):
        """
        Increase or lower stats in battle
        """
        self.boosts[stat] = self.boosts[stat] + level
        if debug:
            print self.name, "'s boosts:", self.boosts
        
    def heal(self, level):
        """
        Restore HP
        """
        healing = (self.get_HP() / 20) * level
        self.HP_rem = self.HP_rem + healing
        if debug:
            print self.name, " healed ", healing, " HP"
            
        if self.HP_rem > self.get_HP():
            self.HP_rem = self.get_HP()
    
    # is there a better way to do this?
    def cap_boosts(self):
        """
        Are your stats too high, or too low?
        """
        if debug:
            print self.boosts
        too_high = []
        too_low = []
        for stat in range(0, 3):
            if self.boosts[stat] > 40:
                too_high.append(stat)
                if debug:
                    print "too high"
                    
            elif self.boosts[stat] < -15:
                too_low.append(stat)
                if debug:
                    print "too low"
                    
        for stat in too_high:
            self.boosts[stat] = 40
            
        for stat in too_low:
            self.boosts[stat] = -15
            
        if debug: 
            print self.boosts    
        
    def check_effectiveness(self, attacker):
        """
        Used to calculate elemental damage taken
        """
        if weaknesses[self.check_ele()] == attacker.check_ele():
            return 1.5
        elif weaknesses[attacker.check_ele()] == self.check_ele():
            return 0.5
        else:
            return 1.0
    
    def calc_DMG(self, attacker, attack_used):
        
        phys_damage = mod(attacker.get_str() - self.get_arm())
        
        ele_damage = mod(attacker.get_ele() * (0.5 * self.check_effectiveness(attacker)))
        
        damage = (phys_damage + ele_damage) * attack_used.get_mult()
        
        if attacker.team.switched_in:
            damage = damage * 0.75
        
        if do_MHC:
            damage = damage * attack_used.calc_MHC()
            
        if debug:
            print "Damage: ", damage
            
        return int(damage)
 
    def take_DMG(self, attacker, attack_used):
        self.HP_rem = int(self.HP_rem - self.calc_DMG(attacker, attack_used))
        
    def check_if_KOed(self):
        """
        Am I dead yet?
        """
        KOed = self.HP_rem <= 0
        
        if KOed:
            print self.name, "is out of the game!"
            
        return KOed

    def use_special(self):
        if self.special != "none":
            self.special.use(self)
            self.team.lose_energy(2)

    """
    Post-battle actions:
        Occur after battle
    """        
    def gain_XP(self, amount):
        """
        Give experience
        """
        self.XP = self.XP + amount
        if self.XP > self.level * 10: 
            self.XP = self.level * 10
        
    def plus_level_set(self):
        self.level_set = self.level_set + 1
        
    def can_level_up(self):
        """
        Make sure you are not blocked by your current level cap
        """
        can = self.level < self.level_set * 5
        if debug:
            print self.name, "can level up:", can
        return can
        
    def level_up(self, levels, display = False):
        """
        Increases level
        """
        
        self.XP = 0
        self.level = self.level + levels
        self.calc_stats()
        self.reset_HP()
        if display:
            self.display_data()
            
    def check_if_LV(self):
        """
        Are you ready to level up?
        """
        if self.level * 10 <= self.XP and self.can_level_up:
            self.level_up(1, True)
        
        elif debug:
            print self.name, "cannot level up."



class Team:
    """
    Used to create teams
    """
    def __init__(self, name, members):
        # Might want to improve this some time later
        self.team = []
        self.name = name
        for new_member in members:
            self.team.append(Warrior(new_member))
    
    def add_member(self, new_member):
        """
        Welcome to the team!
        """
        for member in self.team:
            if new_member[0] == member.name:
                return False
        self.team.append(Warrior(new_member))
        
    def apply_team(self):
        """
        Just so we know who's who
        """
        for member in self.team:
            member.team = self
    
    def find_enemy(self, teams):
        for team in teams:
            if team.name != self.name:
                return team
    
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
        Eventually move this into Warrior
        """
        self.members_rem.remove(member)
    
    def init_energy(self):
        """
        Need... power...
        """
        self.energy = 0
    
    def gain_energy(self, amount = 1):
        """
        Ha ha! More power!
        """
        self.energy = self.energy + amount
        
        if self.energy > 5:
            self.energy = 5
        
    def lose_energy(self, amount):
        """
        WOULD YOU MAKE UP YOUR MIND!
        """
        self.energy = self.energy - amount
        
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
        
    def get_active(self):
        return self.active.name
       
    def show_team(self, exclude_active = False):
        print boarder["top"]
        for member in self.members_rem:
            if exclude_active:
                if member != self.active:
                    print "*", member.name
            else:
                print "*", member.name
        print boarder["bottom"]
        print boarder["break"]
    
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
        print boarder["top"]
        print self.name
        for member in self.team:
            print boarder["break"]
            member.display_data()
        print boarder["bottom"]
        print boarder["break"]
    
    """
    Choices are made using these functions
    """    
    def choose_attack(self, get_return = True):
        """
        How doth thee strike?
        """
        print boarder["top"]
        print "what attack do you want to use?" 
        for attack in attacks:
            print "*", attack.name
        if self.energy >= 2 and self.active.special != "None":
            print "*", self.active.special.name
        decided = False
        print boarder["bottom"]
        print boarder["break"]
        while not decided:
            choice = raw_input(" ")
            for attack in attacks:
                if attack.name.lower() == choice.lower():
                    decided = True
                    if get_return:
                        return attack
                    else:
                        attack.use(self.active)
            if self.energy >= 2 and self.active.special != "None" and (choice.lower() == self.active.special.name.lower() or choice.lower() == "s"):
                decided = True
                if get_return:
                    return self.active.special
                else:
                    self.active.use_special(self)
                
    def choose_switchin(self):
        """
        Who will fight?
        """
        # some repetativeness 
        # man, I hope I spelled that right
        
        if not self.one_left():
            print "Who do you want to bring in?"
            self.show_team(True)
            decided = False
            while not decided:
                choice = raw_input(" ")
                try: choice = int(choice)
                except: choice = str(choice)
                if type(choice) == int:
                    for member in self.members_rem:
                        if choice - 1 == self.members_rem.index(member):
                            self.switch(member)
                            decided = True
                else:
                    for member in self.members_rem:
                        if choice.lower() == member.name.lower():
                            self.switch(member)
                            decided = True
        else:
            self.switch(self.members_rem[0])
            
        print self.get_active(), "up!"
                                        
    def choose_action(self):
        """
        What to do, what to do...
        """
        
        print boarder["top"]
        
        for member in self.members_rem:
            print member.name, member.HP_rem, "/", member.get_HP(), member.check_ele()
        
        print boarder["break"]
            
        print "Currently active:", self.active.name
        print "Energy:", self.energy
        
        print boarder["break"]
        
        print "Active enemy:", self.enemy.active.HP_rem, "/", self.enemy.active.get_HP(), self.enemy.active.check_ele()
        
        print boarder["break"]
        
        if not self.one_left():
            print "What do you wish to do?"
            if self.energy >= 1:
                print "*", "Switch"
            print "*", "Attack"
            print "[]"
            
        print boarder["bottom"]
        print boarder["break"]
        
        decided = False
        
        while not decided:
            if not self.one_left():
                choice = raw_input(" ")
                
            else:
                choice = "attack"
        
            if choice.lower() == "switch": 
                self.choose_switchin()
                self.lose_energy(1)
                self.switched_in = True
                choice = self.choose_attack()
                decided = True
            
            elif choice.lower() == "attack":
                choice = self.choose_attack()
                decided = True
                
        if choice == self.active.special:
            self.lose_energy(2)
        
            
        choice.use(self.active)
           
    def do_turn(self):
        """
        This is where stuff happens
        """
        # Might want to make most of this a seperate function
        rem = []
        for member in self.members_rem:
             if member.check_if_KOed():
                rem.append(member)
        for member in rem:
            self.knock_out(member)
            if self.active == member and self.is_up():
                self.choose_switchin()
        if self.is_up():
            self.switched_in = False
            self.gain_energy()
            
            for member in self.members_rem:
                member.cap_boosts()
                
            self.choose_action()



class Weather:
    """
    This is what makes Maelstrom unique!
    """
    def __init__(self, weather, weather_level, start_message):
        self.weather = (weather, weather_level)
        self.msg = start_message
        
    def do_effect(self, affected):
        """
        I need something witty here
        """
        # could be a better way to handle this...
        weather = self.weather
        
        if weather[0] == "Lightning":
            for person in affected:
                person.inflict(2, weather[1])
            
        if weather[0] == "Wind":
            for person in affected:
                person.inflict(1, weather[1])
            
        if weather[0] == "Hail":
            for person in affected:
                person.inflict(0, -weather[1])
        
        if weather[0] == "Rain":
            for person in affected:
                person.heal(weather[1])
                
    def disp_msg(self):
        """
        A light rain falls...
        """
        print self.msg



class Battle:
    """
    Let the battle begin... later.
    """
    def __init__(self, team_limit, weather = "random"):
        self.teams = []
        self.team_limit = team_limit
        
        # add restrictions later
        if weather == "random":
            weather = random.randrange(0, 12)
            if debug:
                print weather
            
        self.weather = weathers[weather]
        # add weather effects once Weather is implimented
    
    def load_team(self, team):
        """
        Add a team
        """
        self.teams.append(team)
        
        if len(team.team) > self.team_limit:
            print "Select which", self.team_limit, "members you wish to use"
            for member in team.team:
                print "*", member.name
            
            choose = self.team_limit
            team.use = []
            
            while choose > 0:
                add = raw_input("")
                for member in team.team:
                    if add.lower() == member.name.lower() and member not in team.use:
                        team.use.append(member)
                        choose = choose - 1
        else:
            team.use = team.team
        
                        
        if debug:
            print team.use
    
    def check_winner(self):
        """
        Who won?
        """
        for team in self.teams:
            if team.is_up():
                winner = team
        print winner.name, "won!"
    
    def begin(self):
        """
        OK, NOW it begins
        """
        for team in self.teams:
            team.initialize()
            team.enemy = team.find_enemy(self.teams)
            
            for member in team.team:
                if member not in team.use:
                    team.knock_out(member)
                else:
                    member.display_data()
            team.active = team.use[0]
        self.weather.disp_msg()
    
    # work on XP given
    def end(self):
        """
        The stuff that takes place after battle
        """
        for team in self.teams:
            for member in team.team:
                member.gain_XP(10)
                member.check_if_LV()
            
            
    def play(self):
        """
        This is where the action is
        """
        self.begin()
        while self.teams[0].is_up() and self.teams[1].is_up():
            for team in self.teams:
                if team.is_up():
                    team.do_turn()
                    self.weather.do_effect(team.members_rem)
        self.check_winner()
        # remove the next hashtag later
        #self.end()
        
            
"""
Move all this to another document eventually
"""                  


# use these in specials
no_MHC = (0, 8)
no_eff = (0, 0)
act_ene = ("enemy", "act")

slash = Attack(("slash", 1.0, (1, 7), act_ene, no_eff))
jab = Attack(("jab", 0.85, (1, 4), act_ene, (0, 0)))
slam = Attack(("slam", 1.3, (3, 7), act_ene, (0, 0)))

attacks = (slash, jab, slam)

# This works

special_list = {}

for line in specials:
    line = line.split()
    special_list[line[0]] = (line[1], line[2], (line[3], line[4]), (line[5], line[6]), (line[7], line[8]))

if debug:   
    for name, data in special_list.items():
        print name, ":", data



"""
# This works

warrior_list = {}

for line in characters:
    line = line.split()
    warrior_list[line[0]] = (line[0], (line[1], line[2], line[3]), line[4], line[5])
    
for name, data in warrior_list.items():
    print name, ":", data
"""

"""
# This does not work

weather_list = {}

for line in weather:
    line = line.rstrip().split(":")

    # this is wrong, change it to where line[0] is a key for a list, and it appends the data to it
    weather_list[line[0][int(line[1]) -1]] = (line[0], line[1], line[2])
    
for key, value in weather_list.items():
    print key, ":", value    
"""



l_start = ("Lightning", (0, -1, 1), "Lightning", "LAct")
r_start = ("Rain", (0, 1, 1), "Rain", "RAct")
h_start = ("Hail", (0, -1, -1), "Hail", "HAct")
w_start = ("Wind", (0, 1, -1), "Wind", "WAct")



# This is ugly
weathers = (
    Weather("Lightning", 1, "Flashes of light can be seen in the distance..."),
    Weather("Lightning", 2, "Thunder rings not far away..."),
    Weather("Lightning", 3, "The sky rains down its fire upon the field..."),
    
    Weather("Wind", 1, "A gentle breeze whips through..."),
    Weather("Wind", 2, "The strong winds blow mightily..."),
    Weather("Wind", 3, "A twister rips up the land..."),
    
    Weather("Hail", 1, "A light snow was falling..."),
    Weather("Hail", 2, "Hail clatters along the ground..."),
    Weather("Hail", 3, "The field is battered by hail..."),
    
    Weather("Rain", 1, "A light rain falls..."),
    Weather("Rain", 2, "A brisk shower is forecast..."),
    Weather("Rain", 3, "A deluge of water pours forth from the sky...")
    )

test_team = Team("test team", (l_start, h_start))
enemy_team = Team("enemy team", (r_start, w_start))

test_fight = Battle(2)
test_fight.load_team(test_team)
test_fight.load_team(enemy_team)
test_fight.play()
