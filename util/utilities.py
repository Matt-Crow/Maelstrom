import random

debug = False

ELEMENTS = ("lightning", "rain", "hail", "wind")
STATS = ("control", "resistance", "potency", "luck", "energy")

def setInBounds(num, min, max):
    ret = num
    if num < min:
        ret = min
    elif num > max:
        ret = max
    return ret


def roll_perc(base = 0):
    """
    Chooses a random number
    between base and 100,
    use
    roll_perc(self.getStatValue("luck"))
    """
    ret = 100
    base = int(base)
    # don't roll if base is more than 100
    if base > 100:
        Dp.add("Cannot roll: " + str(base) + " is too high")
    else:
        ret = random.randint(base, 100)
        Dp.add("Rolling between " + str(base) + " and 100")
        Dp.add("Rolled " + str(ret))
    Dp.dp()
    return ret

def choose(question, options):
    """
    Returns something from options
    does not convert it to string
    """
    # make sure options is a list
    options = to_list(options)
    names = [str(option) for option in options]
    ret = options[0]
    """
    only bother asking if there
    is more than one option
    """
    if len(options) != 1:
        # output their options
        print(question)
        for num in range(0, len(options)):
            print(str(num + 1) + ": " + names[num])

        #get their input
        ret = options[setInBounds(askIntInput("Enter a number: ") - 1, 0, len(options) - 1)]
        """
        the -1 is because they will enter a number from 1 to len(options),
        so I have to convert it to the corresponding index.
        setInBounds will make any number work
        """
    return ret

"""
Converts an object into a List.
If the object is iterable, adds each element to the new List.
Else, just chucks it on the end of the list.
"""
def to_list(change):
    r = []
    if type(change) == type([1, 2, 3]) or type(change) == type((1, 2, 3) or type(change) == type({"k1":"v1", "k2":"v2"})):
        for item in list(change):
            r.append(item)
    else:
        r.append(change)
    return r

"""
Requests an integer from the user,
displaying the given message.
Repeats this request until the
user enters a valid integer.
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
            print("Invalid input: Enter an integer:")
    return ip


class AbstractOutput:
    """
    This abstract class serves as a base
    for the two output types:
    normal and debug
    """
    msgs = []
    indentation = " "

    @classmethod
    def indent(op):
        op.indentation += "    "

    @classmethod
    def unindent(op):
        op.indentation = " "

    @classmethod
    def add(op, msg):
        msg = to_list(msg)
        for line in msg:
            op.msgs.append(op.indentation + str(line))

    @classmethod
    def reset(op):
        op.msgs = []
        op.unindent()

class Dp(AbstractOutput):
    @staticmethod
    def dp():
        if debug and len(Dp.msgs) is not 0:
            print('\n')
            print("<*DEBUG*>")
            for msg in Dp.msgs:
                print(str(msg))
            Dp.reset()
            input("Press enter or return to continue")
