if __name__ == "__main__":
    print("Oops! You're running from the wrong file!")
    print("Try running Maelstrom.py instead!")
    exit()

from utilities import *

# change this to a seperate file as a fill reading class
script = dict() # this will be used by locations, areas, and levels
def load_script():
    # what key matches up to the next few values?
    current_script_for = None
    for line in open("script.txt"):
        omit = False
        print("Line: " + line)
        
        # Go through the letters in the line...
        for i in range(0, len(line)):
            # a colon symbolizes a change in key for our dictionary
            if line[i] == ':':
                # grab everything prior to the colon
                current_script_for = line[0:i]
                # create a list for that key
                script[current_script_for] = list()
                # don't append the key to its list
                omit = True
        
        if not omit:
            script[current_script_for].append(line)
    
    print(script)

load_script()

class Story:
    def __init__(self, story):
        self.story = to_list(story)
    
    def print_story(self):
        for script in self.story:
            Op.add(script)
            Op.dp()
            pause()

class Location:
    def __init__(self, name, desc, script):
        self.name = name
        self.description = desc
        self.script = Story(script)
        
    def display_data(self):
        Op.add([self.name, self.description])
        Op.dp()
    
    def travel_to(self, player):
        self.script.print_story()
        self.action(player)
        
    def action(self, player):
        return False

class Weather(object):
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
        return
        if self.type == "Lightning":
            for person in affected:
                person.gain_energy(int(self.intensity/20))
                
        if self.type == "Wind":
            for person in affected:
                person.boost("STR", self.intensity/100, 3)
        
        if self.type == "Hail":
            for person in affected:
                person.take_dmg(self.intensity)
        
        if self.type == "Rain":
            for person in affected:
                person.heal(self.intensity)
                     
    def disp_msg(self):
        """
        Print a message showing
        the weather condition
        """
        Op.add(self.msg)
        Op.dp()

# weather need work above and below
# ditch the scripts?
# get rid of the stupid 'use' thing
class Battle(object):
    """
    The Battle class pits 2 teams
    against eachother, 
    initializing them
    and the weather.
    """
    def __init__(self, name, description, script, end, enemy_team, rewards = None):
        self.name = name
        self.description = description
        self.script = Story(script)
        self.final_act = Story(end)
        
        self.forecast = weathers
        
        self.enemy_team = enemy_team
        self.enemy_team.use = self.enemy_team.team
        
        self.rewards = to_list(rewards)
    
    def restrict_weather(self, forecast):
        """
        Since most battles can have any
        weather, it only makes sense to
        exclude it from the constructor,
        so here it is
        """
        self.forecast = to_list(forecast)
    
    def display_data(self):
        Op.add([self.name, self.description])
        
        for member in self.enemy_team.use:
            Op.add("* " + member.name + " LV " + str(member.level) + " " + member.element)
        Op.dp()
    
    def load_team(self, team):
        """
        Load the player's team
        """
        self.player_team = team
        team.use = team.team
        
    # stuff down here
    # add random loot
    def check_winner(self):
        """
        Runs when one
        teams loses all
        members.
        """
        if self.player_team.is_up():
            Op.add(self.player_team.name + " won!")
            Op.dp()
        
            self.final_act.print_story()
            for reward in self.rewards:
                if reward != None:
                    reward.give(self.player_team)
    
    def begin(self):
        """
        Prepare both teams
        for the match.
        """
        self.script.print_story()
        
        self.enemy_team.initialize()
        self.enemy_team.enemy = self.player_team
        
        self.player_team.initialize()
        self.player_team.enemy = self.enemy_team
        
        self.enemy_team.display_data()
        self.player_team.display_data()
        
        if self.forecast[0] == None:
            self.weather = Weather(None, 0, "The land is seized by an undying calm...")
        else:
            if len(self.forecast) == 1:
                num = 0
            else:
                num = random.randrange(0, len(self.forecast) - 1)
                self.weather = self.forecast[num]
        self.weather.disp_msg()
    
    def end(self):
        """
        The stuff that takes place after battle
        """
        xp = self.enemy_team.xp_given()
        for member in self.player_team.use:
            member.gain_XP(xp)
                                    
    def play(self):
        """
        Used to start
        the battle
        """
        self.begin()
        
        while self.enemy_team.is_up() and self.player_team.is_up():
            self.weather.do_effect(self.enemy_team.members_rem)
            # did the weather defeat them?
            if self.enemy_team.is_up():
                self.enemy_team.do_turn()
                # only bother doing player turn if enemy survives
                # so this way we don't get 'ghost rounds'
                self.weather.do_effect(self.player_team.members_rem)
                if self.player_team.is_up():
                    self.player_team.do_turn()           
        self.check_winner()
        self.end()

class Area:
    def __init__(self, name, description, locations, levels):
        self.name = name
        self.description = description
        self.locations = to_list(locations)
        self.levels = to_list(levels)
                
    def display_data(self, player):
        Op.add("Area: " + self.name)
        Op.indent()
        Op.add(self.description)
        Op.dp()
        Op.add("Locations:")
        Op.indent()
        for loc in self.locations:
            loc.display_data()
        Op.unindent()
        Op.add("Levels:")
        Op.indent()
        for level in self.levels:
            level.display_data()
        Op.unindent()
        self.trav_or_play(player)
    
    def trav_or_play(self, player):
        choice = choose("Do you wish to travel to a location, play a level, customize your character, or quit?", ("Location", "Level", "Customize", "Quit"))
        if choice == "Level":
            level_to_play = choose("Which level do you want to play?", self.levels)
            level_to_play.load_team(player)
            level_to_play.play()
        
        elif choice == "Customize":
            player.customize()
            
        elif choice == "Location":
            place_to_go = choose("Where do you want to go?", self.locations)
            place_to_go.travel_to(player)
        
        if choice != "Quit":
            self.display_data(player)

weathers = (
    Weather("Lightning", 40.0, "Flashes of light can be seen in the distance..."),
    Weather("Lightning", 50.0, "Thunder rings not far away..."),
    Weather("Lightning", 60.0, "The sky rains down its fire upon the field..."),
    
    Weather("Wind", 40.0, "A gentle breeze whips through..."),
    Weather("Wind", 50.0, "The strong winds blow mightily..."),
    Weather("Wind", 60.0, "A twister rips up the land..."),
    
    Weather("Hail", 2.5, "A light snow was falling..."),
    Weather("Hail", 5, "Hail clatters along the ground..."),
    Weather("Hail", 7.5, "The field is battered by hail..."),
    
    Weather("Rain", 2.5, "A light rain falls..."),
    Weather("Rain", 5, "A brisk shower is forecast..."),
    Weather("Rain", 7.5, "A deluge of water pours forth from the sky...")
    )