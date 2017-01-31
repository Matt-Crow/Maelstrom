"""
Copyright (c) 2016 Matt Crow 
"""

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
31/10/2016 - 6/10/2016: File work
14/11/2016 - 20/11/2016: Area and general cleanup
21/11/2016 - 1/12/2016: Added AI

Version 0.85
"""

if __name__ == "__main__":
    print "Oops! You're running from the wrong file!"
    print "Try running Maelstrom.py instead!"
    exit()
    
import random

characters = {}
enemies = {}

"""
To do:

Add abilities
Add items

add cancel option
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
    
    print " "
    print question
    
    num = 1
    for option in options:
        try:
            name = option.name  
        except:
            name = option
        
        print str(num) + ": " + name    
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

def load():
    should_load = choose("Do you want to load from a save file?", ("Yes", "No"))
    
    if should_load == "Yes":
        file = Savefile("player_data.txt")
        return file.upload_team()
    
    return Team("Test team", (("Alexandre", 1), ("Rene", 1), ("Ian", 1), ("Viktor", 1)), False, False)

# need to comment this
# work here
class Savefile:
    def __init__(self, file):
        self.file = file
    
    def text_to_dict(self):
        self.dict_file = {}
        file_read = open(self.file, "r")
        for line in file_read:
            if line == " ":
                continue
            line = line.split(":")
            name = line[0].replace("_", " ")
            self.dict_file[name] = {}
            for item in line:
                if item == line[0]:
                    continue
                item = item.split()
                self.dict_file[name][item[0]] = [item[1], item[2], item[3], item[4]]
        
    def upload_team(self):
        self.text_to_dict()
        teams = []
        
        for team in self.dict_file.keys():
            teams.append(team)
        
        choice = choose("Which team do you wish to load?", teams)
        
        members = []
        for member, data in self.dict_file[choice].items():
            members.append((member, int(data[0])))
        # change False to check for team length
        ret = Team(choice, members, False, False)
        
        for member in ret.team:
            for name, array in self.dict_file[choice].items():
                if member.name == name:
                    member.level_set = int(array[1])
                    member.XP = int(array[2])
                    member.stars = int(array[3])
        
        return ret
        
    def update(self, team):
        self.text_to_dict()
        change = {}
        for member in team.team:
            change[member.name] = [str(member.level), str(member.level_set), str(member.XP), str(member.stars)]
        if debug:
            print "Before:", self.dict_file
        
        self.dict_file[team.name] = change
        if debug:
            print "After:", self.dict_file
        
        file = open("player_data.txt", "w")
        for team_name, value in self.dict_file.items():
            new_line = team_name.replace(" ", "_")
            for member in value:
                new_line = new_line + ": " + member + " "
                new_line = new_line + self.dict_file[team_name][member][0] + " "
                new_line = new_line + self.dict_file[team_name][member][1] + " "
                new_line = new_line + self.dict_file[team_name][member][2] + " "
                new_line = new_line + self.dict_file[team_name][member][3] + " "
            new_line = new_line + "\n"
            file.write(new_line)
        file.close()

# balance chances later
# AI for target
class Attack:
    """
    The regular attacks all characters can use
    as well as characters' exclusive Specials
    """
    def __init__(self, name, damage_multiplier, chances, mhc_mults, target, side_effect, energy_cost = 0):
        """
        Copy-paste: 
        name, damage_multiplier, (miss%, crit%), (miss*, crit*), (ally_or_enemy, act_any_all), (eff, eff_LV, eff_dur)  
        """
        self.name = name
        self.mult = float(damage_multiplier)
        self.miss = chances[0]
        self.crit = chances[1]
        self.miss_mult = mhc_mults[0]
        self.crit_mult = mhc_mults[1]
        self.ally_or_enemy = target[0]
        self.act_any_all = target[1]
        self.eff = side_effect[0]
        self.eff_LV = side_effect[1]
        self.eff_dur = side_effect[2]
        self.energy_cost = energy_cost   
        
    def calc_MHC(self):
        """
        Used to calculate hit type
        """
        rand = random.randint(1, 100)
        if debug:
            print "rand in calc_MHC: ", rand
            print "Crit:", 100 - self.crit
            print "Miss:", self.miss
            
        if rand <= self.miss:
            print "A glancing blow!"
            return self.miss_mult
            
        elif rand >= 100 - self.crit:
            print "A critical hit!"
            return self.crit_mult
            
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
        
        targets = []
        
        if self.act_any_all == "act":
            targets.append(target_team.active)
            
        elif self.act_any_all == "all":
            for member in target_team.members_rem:
                targets.append(member)
                
        elif self.act_any_all == "any":
            if user.team.AI:
                highest = 0
                best = None
                options = []
                if user.team.switched_in:
                    m = 0.75
                else:
                    m = 1.0
                for member in target_team.members_rem:
                    damage = member.calc_DMG(user, self) * m
                    if damage >= member.HP_rem:
                        options.append(member)
                    if damage >= highest:
                        highest = damage
                        best = member
                if len(options) >= 1:
                    hit = target_team.members_rem[random.randint(0, len(options) - 1)]
                else:
                    hit = best
            else:
                hit = choose("Who do you wish to hit?", target_team.members_rem)
            targets.append(hit)
                        
        for warrior in targets:               
            warrior.take_DMG(user, self)
            if self.eff != 0:
                warrior.boost(self.eff, self.eff_LV, self.eff_dur)
        
        user.team.lose_energy(self.energy_cost)

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

    def __init__(self, name, level):
        """
        base stats: (def ratio, res ratio, con ratio)
        """
        self.name = name
        if name in characters:
            data = characters[name]
        elif name in enemies:
            data = enemies[name]
        else:
            data = (0, 0, 0)
        self.base_stats = data[0]
        self.element = data[1]
        self.special = data[2]
        self.level = level
        self.XP = 0
        self.level_set = 1
        self.stars = 0
       
    def calc_stats(self):
        """
        Calculate a character's stats
        """
        
        def_mult = 1.0 + self.base_stats[0] * 0.025
        off_mult = 1.0 - self.base_stats[0] * 0.025
        if debug:
            print "def_mult: " + str(def_mult)
            print "off_mult: " + str(off_mult)
        
        base_HP = def_mult * 100
        
        RESRAT = 0.5 + self.base_stats[1] * 0.05
        ARMRAT = 1.0 - RESRAT
        
        if debug:
            print "RESRAT: " + str(RESRAT)
            print "ARMRAT: " + str(ARMRAT)
        
        # default is 0.5, so 20 base
        base_res = RESRAT * def_mult * 40
        base_arm = ARMRAT * def_mult * 40
        
        # offensive stats
        
        base_dmg = off_mult * 20
        
        CONRAT = 0.5 + self.base_stats[2] * 0.05
        STRRAT = 1.0 - CONRAT
        
        if debug:
            print "CONRAT: " + str(CONRAT)
            print "STRRAT: " + str(STRRAT)
            
        # once again, default is 0.5
        base_con = CONRAT * off_mult * 40
        base_str = STRRAT * off_mult * 40
        
        self.max_HP = base_HP * (1 + self.level * 0.1)
        self.dmg = base_dmg * (1 + self.level * 0.2) 
        self.arm = base_arm * (1 + self.level * 0.2) 
        self.res = base_res * (1 + self.level * 0.2) 
        self.str = base_str * (1 + self.level * 0.2) 
        self.con = base_con * (1 + self.level * 0.2) 
    
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
        self.calc_stats()
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
        print "HP: " + str(int(self.max_HP))
        print "DMG:" + str(int(self.dmg))
        print "STR:" + str(int(self.str))
        print "ARM:" + str(int(self.arm))
        print "CON:" + str(int(self.con))
        print "RES:" + str(int(self.res))
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
        
        if percent > 0:
            msg = " restored "
        elif percent < 0:
            msg = " lost "
        else:
            return
        
        print self.name + msg + str(abs(int(healing))) + " HP"
            
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
    
    def calc_DMG(self, attacker, attack_used):
        
        phys_damage = attacker.get_str() / self.get_arm()
        
        ele_damage = (attacker.get_con() * self.check_effectiveness(attacker)) / self.get_res()
        
        damage = (phys_damage + ele_damage) / 2 * attack_used.mult * attacker.get_dmg()
        
        if attacker.team.switched_in:
            damage = damage * 0.75
        """    
        if debug:
            print "Physical Mult:", phys_damage
            print "Elemental Mult:", ele_damage
            print "Raw damage:", (phys_damage + ele_damage) / 2
            print "Damage before MHC:", damage
        """    
        return int(damage)
        
    def take_DMG(self, attacker, attack_used):
        print " "
        dmg = self.calc_DMG(attacker, attack_used)
        if do_MHC:
            dmg = dmg * attack_used.calc_MHC()
        print attacker.name + " struck " + self.name + " for " + str(int(dmg)) + " damage using " + attack_used.name + "!"
        self.HP_rem = int(self.HP_rem - dmg)
        cont = raw_input("Press enter/return to continue")
        
    def check_if_KOed(self):
        """
        Am I dead yet?
        """
        return self.HP_rem <= 0
    
    def can_spec(self):
        if debug:
            print "Current energy: " + str(self.team.energy)
            print "Special energy cost: " + str(self.special.energy_cost)
        return self.team.energy >= self.special.energy_cost
    
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
        if self.team.AI:
            return
        
        self.XP = self.XP + amount
        if self.XP >= self.level * 10: 
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

class Contract:
    def __init__(self, comes_with):
        """
        A contract is used to hire a
        new character, or boost an old
        one.
        """
        self.name = "Contract"
        self.poss = []
        if comes_with == None:
            if debug:
                print "No set characters in contract."
        elif type(comes_with) == type("This is a string"):
            self.poss.append(comes_with)
        else:
            for character in comes_with:
                self.poss.append(character)
        
        poss = []
        for key in characters.keys():
            poss.append(key)
        size = len(self.poss)
        while size < 4:
            num = random.randint(1, len(poss) - 1)
            if poss[num] in self.poss:
                continue
            self.poss.append(poss[num])
            size += 1
            
    def use(self):
        """
        Ask the player if they want
        a hint, then let them choose
        a character.
        RETURNS THE ANSWER
        DOES NOT CHANGE THE PLAYER'S TEAM
        """
        print "*Recruiting*"
        char = []
        for member in self.poss:
            char.append(Character(member, 1))
            
        for member in char:
            member.calc_stats()
            
        pick_or_hint = choose("Do you want a hint before choosing?", ("Yes", "No"))
        if pick_or_hint == "Yes":
            hint = choose("What do you want to see?", ("HP", "RES", "ARM", "CON", "STR", "DMG", "Element"))
            
            for member in char:
                hints = {
                    "HP" : int(member.max_HP), 
                    "RES" : int(member.res),
                    "ARM" : int(member.arm),
                    "CON" : int(member.con),
                    "STR" : int(member.str),
                    "DMG" : int(member.dmg),
                    "Element" : member.element.name
                }
                print hints[hint]
                    
        new = choose("Who do you want to hire?", ("?", "??", "???", "????"))
        if new == "?":
            return (self.poss[0], 1)
        elif new == "??":
            return (self.poss[1], 1)
        elif new == "???":
            return (self.poss[2], 1)
        else:
            return (self.poss[3], 1)

class Tavern:
    def __init__(self, name):
        self.name = name
    
    def recruit(self, team, contracts):
        print "So, you wan't to hire out another warrior, eh?"
        print "Now let me see..."
        if len(contracts) == 0:
            print "Sorry, but it looks like you don't have any contracts."
            print "Come back when you have one, and then we'll talk."
        else:
            print "Well well well, and here I thought you weren't credibly."
            print "How about you take a look at who we got here?"
            
            con = choose("Which contract do you want to use?", contracts)
            team.add_member(con.use())

class Team:
    """
    Teams are used to group characters
    together so that the program knows
    who are enemies, and who are allies.
    """
    def __init__(self, name, members, single, AI = False):
        self.team = []
        self.name = name
        self.AI = AI
        
        if single:
            self.team.append(Character(members[0], members[1]))
            return
        
        for new_member in members:
            self.team.append(Character(new_member[0], new_member[1]))
        
    def add_member(self, new_member):
        """
        Add a member to a team.
        """
        for member in self.team:
            if new_member[0] == member.name:
                member.stars += 1
                print member.name + "'s stats were boosted!"
                member.init_for_battle()
                member.display_data()
                return False
        self.team.append(Character(new_member[0], new_member[1]))
        print new_member[0] + " joined " + self.name + "!"
        self.team[-1].init_for_battle()
        self.team[-1].display_data()
        
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
        if self.AI:
            self.active = self.use[0]
            return
        lead = choose("Who do you want to lead with?", self.use)
        
        self.active = lead
        
    def switch(self, member):
        """
        You're up!
        """
        self.active = member
    
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
    AI stuff
    """
    def should_switch(self):
        """
        First, check if our active can KO
        """
        if self.enemy.active.calc_DMG(self.active, slam) >= self.enemy.active.HP_rem:
            if debug:
                print self.active.name + " can KO " + self.enemy.active.name + " with Slam"
            return "Attack"
        if self.enemy.active.calc_DMG(self.active, self.active.special) >= self.enemy.active.HP_rem and self.active.can_spec():
            if debug:
                print self.active.name + " can KO " + self.enemy.active.name + " with " + self.active.special.name
            return "Attack"
        # check if your active can benchhit
        if self.active.special.act_any_all != "act":
            for member in self.enemy.members_rem:
                if member.calc_DMG(self.active, self.active.special) >= member.HP_rem and self.active.can_spec():
                    if debug:
                        print self.active.name + " can KO " + member.name + " with " + self.active.special.name
                    return "Attack"
        
        """
        Second, check if an ally can KO 
        """
        for member in self.members_rem:
            if self.enemy.active.calc_DMG(member, slam) * 0.75 >= self.enemy.active.HP_rem:
                return "Switch"
            if self.enemy.active.calc_DMG(member, member.special) * 0.75 >= self.enemy.active.HP_rem and member.can_spec():
                return "Switch"
            # Check if we are strong against them
            if self.active.element.name == self.enemy.active.element.weakness:
                return "Attack"
        
        """
        Lastly, if all else fails, run for your life
        """
        if self.active.element.weakness == self.enemy.active.element.name and not self.one_left() and self.energy >= 2:
            return "Switch"
        # Default
        return "Attack"
    
    # comment   
    def who_switch(self):
        """
        Used to help the AI
        decide who to switch in
        """
        can_ko = []
        """
        Can anyone KO?
        """
        for member in self.members_rem:
            if self.enemy.active.calc_DMG(member, slam) * 0.75 >= self.enemy.active.HP_rem:
                can_ko.append(member)
            elif self.enemy.active.calc_DMG(member, self.active.special) * 0.75 >= self.enemy.active.HP_rem and member.can_spec():
                can_ko.append(member)
        if debug:
            for member in can_ko:
                print member.name
            print "can KO"
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
        """
        Check for advantages
        """
        at_adv = []
        for member in array:
            if member.element.name == self.enemy.active.element.weakness:
                at_adv.append(member)
        if debug:
            for member in at_adv:
                print member.name
            print "are at advantage"
        
        # comment here
        """
        If someone is at advantage 
        AND can KO,
        use them.
        If multiple people can KO AND are at advantage,
        use them.
        """
        strong_and_ko = []
        for member in at_adv:
            if member in can_ko:
                strong_and_ko.append(member)
        
        if len(strong_and_ko) == 1:
            return strong_and_ko[0]
        if len(strong_and_ko) > 1:
            rand = random.randint(0, len(strong_and_ko) - 1)
            print rand
            return strong_and_ko[rand]
        if len(can_ko) > 1:
            rand = random.randint(0, len(can_ko) - 1)
            print rand
            return can_ko[rand]
        if len(at_adv) == 1:
            return at_adv[0]
        if len(at_adv) > 1:
            rand = random.randint(0, len(at_adv) - 1)
            print rand
            return at_adv[rand]
        
        """
        Check for disadvantages
        """
        not_at_dis = []
        for member in self.members_rem:
            if self.enemy.active.element.name != member.element.weakness:
                not_at_dis.append(member)
        if debug:
            for member in not_at_dis:
                print member.name
            print "are not at disadvantage"
        if len(not_at_dis) == 1:
            return not_at_dis[0]
        if len(not_at_dis) > 1:
            rand = random.randint(0, len(not_at_dis) - 1)
            return not_at_dis[rand]
        
        rand = random.randint(0, len(self.members_rem) - 1)
        return self.members_rem[rand]  
    
    # work on specials
    def what_attack(self):
        """
        Used to help the AI
        choose what attack
        to use
        """
        if self.switched_in:
            sw = 0.75
        else:
            sw = 1.0
        """
        Can you get multiple KOes?
        """
        if self.active.can_spec() and self.active.special.act_any_all == "all":
            koes = 0
            for member in self.enemy.members_rem:
                if member.calc_DMG(self.active, self.active.special) * sw >= member.HP_rem:
                    koes += 1
            if koes >= 2:
                return self.active.special
        """
        Can you get a KO?
        """
        if self.enemy.active.calc_DMG(self.active, slash) * sw >= self.enemy.active.HP_rem:
            return slash
        if do_MHC:
            if self.enemy.active.calc_DMG(self.active, slam) * sw >= self.enemy.active.HP_rem:
                return slam
        if self.active.can_spec():
            if self.active.special.act_any_all == "any":
                if self.enemy.active.calc_DMG(self.active, self.active.special) * sw >= self.enemy.active.HP_rem:
                    return self.active.special
            if self.enemy.active.calc_DMG(self.active, self.active.special) * sw >= self.enemy.active.HP_rem:
                return self.active.special
        """
        If you cannot KO...
        """
        if self.active.can_spec():
            return self.active.special
         
        # default to jab (or slash if no MHC)
        
        if do_MHC:
            return jab
        else:
            return slash
            
    """
    Choices are made using these functions
    """    
    def choose_attack(self):
        """
        How doth thee strike?
        """
        if not self.AI:
            attack_options = []
        
            # to avoid editting attacks...
            if do_MHC:
                for attack in attacks:
                    attack_options.append(attack)
            else:
                attack_options.append(slash)
        
            if self.active.can_spec() and self.active.special != None:
                attack_options.append(self.active.special) 
        
            choice = choose("What attack do you wish to use?", attack_options)
        
        else:
            if debug:
                print "AI is choosing attack..."
            choice = self.what_attack()
        
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
        
        if not self.AI:
            switch_for = choose("Who do you want to bring in?", choices)
        else:
            if debug:
                print "AI is deciding..."
            switch_for = self.who_switch()
        
        self.switch(switch_for)
          
        print self.active.name, "up!"
                                        
    def choose_action(self):
        """
        What to do, what to do...
        """
        print self.name
        print " "
        for member in self.members_rem:
            print member.name + " " + str(member.HP_rem) + "/" + str(member.get_HP()) + " " + member.element.name
            
        print "Currently active: " + self.active.name
        print "Energy: " + str(self.energy)
        print "Active enemy: " + self.enemy.active.name + " " + str(self.enemy.active.HP_rem) + "/" + str(self.enemy.active.get_HP()) + " " + self.enemy.active.element.name
        
        choices = ["Attack"]
        
        if (not self.one_left()) and self.energy >= 2:
            choices.append("Switch")
        
        if not self.AI:
            attack_switch = choose("What do you wish to do?", choices)
        else:
            if len(choices) == 1:
                pass
            if debug:
                print "AI is deciding..."
            attack_switch = self.should_switch()
        
        if attack_switch == "Switch":
            self.choose_switchin()
            self.lose_energy(2)
            self.switched_in = True
        self.choose_attack()
        
    def do_turn(self):
        """
        This is where stuff happens
        """
        print ""
        print ""
        print ""
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
            
            self.gain_energy(2)
            
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

class Story:
    def __init__(self, story):
        if story == None:
            self.story = []
        elif type(story) != type(["This", "is a", "list"]) and type(story) != type(("Tuples", "are so", "cute!")):
            self.story = [story]
        else:
            self.story = story
        
        
    def print_story(self):
        for script in self.story:
            print script
            go = raw_input("Press enter/return to continue")

class Battle:
    """
    The Battle class pits 2 teams
    against eachother, 
    initializing them
    and the weather.
    """
    def __init__(self, name, description, script, end, team_size, weather_list):
        """
        Maximum team size,
        Weather should be improved
        """
        self.teams = []
        self.name = name
        self.description = description
        self.script = Story(script)
        self.final_act = Story(end)
        self.team_size = team_size
        self.forecast = weather_list
    
    def display_data(self):
        print " "
        print self.name
        print self.description
        for member in self.teams[0].use:
            print "* " + member.name + " LV " + str(member.level) + " " + member.element.name
    
    def load_team(self, team):
        """
        Add a team 
        to the battle
        """
        self.teams.append(team)
        
        if len(team.team) > self.team_size:
            print "Select which " + str(self.team_size) + " members you wish to use"
            num = self.team_size
            team.use = []
            roster = []
            for member in team.team:
                roster.append(member)
            
            while num > 0:
                add = choose("Select member to add:", roster)
                
                for member in team.team:
                    if add == member:
                        team.use.append(member)
                        roster.remove(member)
                        num = num - 1
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
        self.script.print_story()
        
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
        try:
            num = random.randrange(0, len(self.forecast) - 1)
            self.weather = self.forecast[num]
        except:
            if self.forecast == None:
                self.forecast = Weather(None, 0, "The land is seized by an undying calm...")
            self.weather = self.forecast
        
        self.weather.disp_msg()
    
    def end(self):
        """
        The stuff that takes place after battle
        """
        for team in self.teams:
            for member in team.use:
                xp = team.enemy.xp_given()
                member.gain_XP(xp)
        print " "
        self.final_act.print_story()
                    
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
                if not team.is_up():
                    break      
        self.check_winner()
        self.end()
# needs improve    
class Area:
    """
    """
    def __init__(self, name, description, levels):
        self.name = name
        self.description = description
        self.levels = []
        if type(levels) != type(("x", "y")):
            self.levels.append(levels)
        else:
            for level in levels:
                self.levels.append(level)
    # improve this            
    def display_data(self, player_team):
        print self.name
        print self.description
        for level in self.levels:
            level.display_data()
        level_to_play = choose("Which level do you want to play?", self.levels)
        level_to_play.load_team(player_team)
        level_to_play.play()
        self.display_data(player_team)

no_MHC = (0, -1)
no_MHC_mult = (1, 1)
no_eff = (0, 0, 0)
act_ene = ("enemy", "act")
        
slash = Attack("slash", 1.0, (20, 20), (0.75, 1.25), act_ene, no_eff)
jab = Attack("jab", 0.85, (15, 40), (0.8, 1.88), act_ene, no_eff)
slam = Attack("slam", 1.3, (30, 10), (0.69, 1.2), act_ene, no_eff)

attacks = (slash, jab, slam)

from maelstrom import do_MHC, debug 
