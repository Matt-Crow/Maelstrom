from maelstrom.campaign.area import Area
from maelstrom.gameplay.combat import playLevel
from maelstrom.inputOutput.screens import Screen
from maelstrom.loaders.characterLoader import EnemyLoader
from maelstrom.util.user import User



def chooseUserAreaAction(user: User, area: "Area", enemy_loader: EnemyLoader):
    screen = Screen(area.name)
    screen.add_body_row(area.getDisplayData())

    options = []
    for level in area.levels:
        options.append(level)
    options.append("quit")
    choice = screen.display_and_choose("Choose a level to play:", options)

    if choice is not "quit":
        playLevel(choice, user, enemy_loader)
