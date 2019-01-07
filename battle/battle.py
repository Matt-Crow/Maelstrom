from navigate import *
from utilities import *
from file import File
from weather import Weather
from teams import EnemyTeam
from enemies import *
from story import Story
from output import Op

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
    
    def get_data(self):
        """
        gets data for outputting
        """
        ret = [self.name, "\t" + self.description]
        for member in self.enemy_team.team:
            ret.append("\t* " + member.get_short_desc())
        return ret
    
    def __str__(self):
        return self.name

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
            Op.display()

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
        Op.add(self.weather.get_msg())
        Op.display()

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
            pass
            #enemy_names.append(elemental_enemies[random.randint(0, len(elemental_enemies) - 1 )])
        return Battle("Random encounter", enemy_names, 1)
