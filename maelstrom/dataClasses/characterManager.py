from maelstrom.dataClasses.character import Character
from maelstrom.inputOutput.screens import Screen



def manageCharacter(character: Character):
    options = ["Quit", character]
    screen = Screen(f'Manage {character.name}')

    if True: # needs to check it items available
        options.append("Equipped items")

    screen.add_body_rows([str(item) for item in character.equippedItems])
    options.extend(character.equippedItems)

    # todo: add option to change passives
    # todo: add option to change actives

    options.reverse()
    customize = screen.display_and_choose("What do you want to customize?", options)
    if customize != "Quit":
        if customize == "Equipped items":
            raise Exception("todo move item choosing to user instead of character")
        else:
            customize.customizeMenu()
