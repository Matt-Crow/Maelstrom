class Game:
    """
    The Game class is used to store data on the game the user is currently playing,
    so this way, there don't have to be any globals.
    """
    def __init__(self):
        self.player = None
        #gameType (Maelstrom, or other rpg)
