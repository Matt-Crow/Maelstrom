from util.output import Op
from file import File, PlayerSaveFile
from battle.teams import PlayerTeam
from utilities import choose

class Game:
    """
    The Game class is used to store data on the game the user is currently playing,
    so this way, there don't have to be any globals.
    """
    def __init__(self):
        self.player = None
        self.exit = False
        #gameType (Maelstrom, or other rpg)
    
    def run(self):
        """
        Begins the program
        """
        while not self.exit:
            if self.player == None:
                self.main_menu()
            else:
                print("Player login works. My work here is done.")
                self.exit = True
    
    def main_menu(self):
        """
        Displayes the main menu
        """
        Op.add("MAELSTROM")
        Op.display()
        action = choose("Choose an option: ", ["Play", "About", "Quit"])
        if action == "Play":
            self.login_menu()
        elif action == "Quit":
            self.exit = True
    
    def login_menu(self):
        """
        Asks the user to log in
        """
        users = File("users/users.txt").get_lines()
        
        options = users.copy()
        options.append("None of these")
        
        user_name = " "
        
        action = choose("Do you wish to load a game, or start a new one?", ["Create game", "Load game"])
        if action == "Load game":
            user_name = choose("Which user are you?", options)
        #TODO: how to add user?
        
        self.login_user(user_name)
    
    def login_user(self, user_name):
        """
        Play a game as the given user
        """
        data = PlayerSaveFile("users/" + user_name.replace(" ", "_") + ".txt")
        if data.error:
            print("cannot find save file for " + user_name)
        else:
            #change this later
            self.player = PlayerTeam("Player team", {"name": "Alexandre", "data": ((0, 0, 0, 0, 0), "lightning"), "level": 1})
            self.player.team[0].read_save_code(data.get_lines())
            self.player.initialize()
            self.player.list_members()