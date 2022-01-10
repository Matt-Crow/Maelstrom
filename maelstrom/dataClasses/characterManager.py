from maelstrom.inputOutput.screens import Screen



def manageCharacter(character: "Character"):
    options = ["Quit", character]
    screen = Screen()
    screen.setTitle(f'Manage {character.name}')

    if True: # needs to check it items available
        options.append("Equipped items")

    for item in character.equippedItems:
        screen.addBodyRow(str(item))
        options.append(item)

    # todo: add option to change passives
    # todo: add option to change actives

    options.reverse()

    for option in options:
        screen.addOption(option)

    customize = screen.displayAndChoose("What do you want to customize?")
    if customize != "Quit":
        if customize == "Equipped items":
            raise Exception("todo move item choosing to user instead of character")
        else:
            customize.customizeMenu()
