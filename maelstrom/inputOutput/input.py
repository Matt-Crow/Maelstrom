"""
This module gathers user input

it is used by screens.py
"""



from maelstrom.inputOutput.output import output



"""
Returns an element from options
"""
def choose(prompt: str, options: "List<any>", displayOptions=True)->"any":
    options = toList(options)
    names = (str(option) for option in options)
    chosen = options[0] # will purposely fail if no options

    """
    only bother asking if there is more than one option
    """
    if len(options) > 1:
        output(prompt)

        if displayOptions:
            for i in range(0, len(options)):
                output(f'{i + 1}: {names[i]}')

        # get user input
        ip = askIntInput(f'Enter a number [1 - {len(options)}]: ')
        ip -= 1 # convert choice number to index in array

        while ip < 0 or len(options) <= ip:
            ip = askIntInput(f'Enter a number [1 - {len(options)}]: ') - 1

        chosen = options[ip]

    return chosen


def toList(obj: "any")->"List<any>":
    asList = []
    try:
        for i in iter(obj):
            asList.append(i)
    except TypeError as nopeNotIterable:
        asList.append(obj)
    return asList



"""
Requests an integer from the user, displaying the given message. Repeats this
request until the user enters a valid integer.
"""
def askIntInput(msg: str)->int:
    ip = " "
    valid = False
    while not valid:
        ip = input(msg)
        try:
            ip = int(float(ip))
            valid = True
        except:
            output("Invalid input: Enter an integer:")
    return ip
