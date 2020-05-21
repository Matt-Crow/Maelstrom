from output import Op
from teams import PlayerTeam, AbstractTeam
from character import AbstractCharacter
from utilities import choose, ELEMENTS
from area import Area
import json
from fileSystem import getUserList

from generateData import generateEnemies

"""
The Game class is used to store data on the game the user is currently playing,
so this way, there don't have to be any globals.
"""
class Game:
    def __init__(self):
        self.player = None
        self.exit = False

    def test(self):
        Op.add(getUserList())
        Op.display()
        generateEnemies()
        defaultPlayer = AbstractCharacter.createDefaultPlayer()
        team = PlayerTeam(
            name="Default team",
            member=defaultPlayer
        )
        Area.createDefaultArea().chooseAction(team)

    """
    Begins the program
    """
    def run(self):
        while not self.exit:
            if self.player == None:
                self.mainMenu()
            else:
                Area.loadDefault().chooseAction(self.player)
                self.exit = True #since Area will run until the user chooses to quit.
                raise Exception("Still need to add player saving!")
                #self.player.save() fileSystem.saveUser(self.player)

    """
    Displayes the main menu
    """
    def mainMenu(self):
        Op.add("MAELSTROM")
        Op.display()
        action = choose("Choose an option: ", ["Play", "About", "Quit"])
        if action == "Play":
            self.loginMenu()
        elif action == "About":
            pass # do nothing yet
        else:
            self.exit = True

    """
    Asks the user to log in
    """
    def loginMenu(self):
        options = getUserList()
        options.append("None of these")

        user_name = " "

        action = choose("Do you wish to load a game, or start a new one?", ["Create game", "Load game"])
        if action == "Load game":
            user_name = choose("Which user are you?", options)
            if user_name == 'None of these':
                self.new_user_menu()
                self.loginMenu()
            else:
                self.login_user(user_name)
        else:
            self.new_user_menu() #logs in if successful


    def login_user(self, user_name):
        """
        Play a game as the given user
        """
        self.player = AbstractTeam.loadTeam('users/' + user_name.replace(" ", "_").lower() + '.json')
        self.player.initForBattle()
        self.player.displayData()


    def new_user_menu(self):
        """
        Creates the menu for creating a new user
        """
        name = input('What do you want your character\'s name to be? ')
        element = choose('Each character has elemental powers, what element do you want yours to control?', ELEMENTS)
        result = self.create_user(name, element)
        print(result)
        if result == 'User added successfully!':
            self.login_user(name)
        else:
            self.new_user_menu()


    def create_user(self, user_name: str, element: str) -> str:
        """
        Adds a user.
        Returns a message based on if the profile creation was successful
        """
        ret = 'User added successfully!'
        success = True

        with open('users/users.txt', 'rt') as file:
            if user_name in file.read():
                ret = 'The name ' + user_name + ' is already taken.'
                success = False


        if success:
            character = AbstractCharacter.createDefaultPlayer(user_name, element)
            PlayerTeam(user_name, character).save()

            with open('users/users.txt', 'a') as file:
                file.write(user_name + '\n')

        return ret
