from maelstrom.gameplay.combat import playLevel
from maelstrom.inputOutput.screens import Screen



def chooseUserAreaAction(user: "User", area: "Area"):
    screen = Screen()
    screen.setTitle(area.name)
    screen.addBodyRow(area.getDisplayData())

    options = []
    for level in area.levels:
        options.append(level)
    options.append("quit")

    for option in options:
        screen.addOption(option)

    choice = screen.displayAndChoose("Choose a level to play:")

    if choice is not "quit":
        playLevel(choice, user)