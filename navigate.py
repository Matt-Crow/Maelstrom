from utilities import *
from stat_classes import *
from file import *
from enemies import *
from teams import *
import random

script_file = File("script.txt")
script_file.create_dict(':')

class Story:
    def __init__(self, story):
        self.story = to_list(story)
    
    def print_story(self):
        for script in self.story:
            Op.add(script)
            Op.dp()
            pause()

class Location:
    def __init__(self, name):
        self.name = name
        
        self.all_text = script_file.grab_key(name)
        self.description = " "
        self.script = Story(" ")
        
        script_list = list()
        
        mode = None
        for line in self.all_text:
            if contains(line, File.description_key):
                self.description = ignore_text(line, File.description_key)
            
            if contains(line, File.script_key):
                mode = "script"
            
            if mode == "script":
                script_list.append(ignore_text(line, File.script_key))
            
            if len(script_list) is not 0:
                self.script = Story(script_list)
        
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
    
    types = {
        "lightning": "The sky rains down its fire upon the field...",
        "rain": "A deluge of water pours forth from the sky...",
        "hail": "A light snow was falling...",
        "wind": "The strong winds blow mightily...",
        None: "The land is seized by an undying calm..."
    }
    
    def __init__(self, type, intensity):
        """
        The type determines what sort of effect will
        be applied to all participants in a battle.
        The intensity is how potent the effect will be.
        The msg is what text will show to help
        the player determine the weather.
        """
        self.intensity = intensity
        
        if type in Weather.types:
            self.type = type
        else:
            self.type = Weather.random_type()
        
        self.msg = Weather.types[type]
            
    def do_effect(self, affected):
        """
        Apply stat changes 
        to a team
        """
        if self.type == "lightning":
            for person in affected:
                person.gain_energy(self.intensity)
                
        if self.type == "wind":
            for person in affected:
                person.boost(Boost("control", self.intensity * 5, 1, "Weather"))
        
        if self.type == "hail":
            for person in affected:
                person.harm(self.intensity * 4)
        
        if self.type == "rain":
            for person in affected:
                person.heal(self.intensity * 3)
                     
    def disp_msg(self):
        """
        Print a message showing
        the weather condition
        """
        Op.add(self.msg)
        Op.dp()
    
    @staticmethod
    def generate_random():
        return Weather(Weather.random_type(), Weather.random_intensity())
    
    @staticmethod
    def random_type():
        return random.choice(Weather.types.keys())
    
    @staticmethod
    def random_intensity():
        return random.randint(1, 5)

class Battle(object):
    """
    The Battle class pits 2 teams
    against eachother, 
    initializing them
    and the weather.
    """
    def __init__(self, name, enemy_names, enemy_levels, rewards = None):
        self.name = name
        self.all_text = script_file.grab_key(name)
        
        self.description = " "
        self.script = Story(" ")
        self.final_act = Story(" ")
        
        script_list = list()
        final_act_list = list()
        
        mode = None
        for line in self.all_text:
            if contains(line, File.description_key):
                self.description = ignore_text(line, File.description_key)
            
            if contains(line, File.prescript_key):
                mode = "pre"
            
            if contains(line, File.postscript_key):
                mode = "post"
                
            if mode == "pre":
                script_list.append(ignore_text(line, File.prescript_key))
                
            elif mode == "post":
                final_act_list.append(ignore_text(line, File.postscript_key))
            
            if len(script_list) is not 0:
                self.script = Story(script_list)
            if len(final_act_list) is not 0:
                self.final_act = Story(final_act_list)
        
        self.forecast = to_list(None)
        
        self.enemy_team = EnemyTeam(enemy_names, enemy_levels)
        
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
        
        for member in self.enemy_team.team:
            Op.add("* " + member.name + " LV " + str(member.level) + " " + member.element)
        Op.dp()
    
    def load_team(self, team):
        """
        Load the player's team
        """
        self.player_team = team
        
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
        
        self.weather = Weather.generate_random()
        
        if self.forecast[0] is not None:
            num = 0
            if len(self.forecast) > 1:
                num = random.randrange(0, len(self.forecast) - 1)
            self.weather = self.forecast[num]
        self.weather.disp_msg()
    
    def end(self):
        """
        The stuff that takes place after battle
        """
        xp = self.enemy_team.xp_given()
        for member in self.player_team.team:
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
    
    @staticmethod
    def generate_random():
        """
        Creates a random level
        """
        enemy_names = []
        num_enemies = random.randint(1, 4)
        for i in range(0, num_enemies):
            enemy_names.append(elemental_enemies[random.randint(0, len(elemental_enemies) - 1 )])
        return Battle("Random encounter", enemy_names, 1)
        
class Area:
    def __init__(self, name, locations, levels):
        self.name = name
        self.description = ignore_text(script_file.grab_key(name)[0], File.description_key)
        self.locations = to_list(locations)
        self.levels = to_list(levels)
        self.levels.append(Battle.generate_random())
                
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