import random

debug = False

ELEMENTS = ("lightning", "rain", "hail", "wind")
STATS = ("control", "resistance", "potency", "luck", "energy")

def ignore_text(word, ignore):
    """
    Returns a string, if ignore
    exists in that string, remove
    it from the returned string
    """
    ret = ""
    letters_found = 0
    found_so_far = ""

    # go through the word...
    for letter in range(0, len(word)):
        # is the current letter equal to the next letter in ignore?
        if word[letter] == ignore[letters_found]:
            # keep track of what we've found, just in case
            found_so_far += word[letter]
            letters_found += 1
            # have we found the whole word?
            if letters_found == len(ignore):
                # ignore it
                letters_found = 0
                found_so_far = ""
        else:
            # don't ignore it
            letters_found = 0
            ret += found_so_far
            found_so_far = ""
            ret += word[letter]
    return ret

def mod(num):
    """
    A useful little guy
    """
    if num < 1:
        num = 1
    return num

def set_in_bounds(num, min, max):
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
    names = get_names_str(options)
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
        Ip.askInt("Enter a number: ") # automatically checks for number
        ret = options[set_in_bounds(Ip.getInt() - 1, 0, len(options) - 1)]
        """
        the -1 is because they will enter a number from 1 to len(options),
        so I have to convert it to the corresponding index.
        set_in_bounds will make any number work
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

def get_names_str(list):
    """
    Makes sure all the elements
    in the list are strings
    """
    ret = []
    for object in list:
        ret.append(str(object))
    return ret

class Ip:
    """
    Input
    """
    strings = []
    ints = []

    @staticmethod
    def askStr(msg):
        Ip.strings.append(raw_input(msg))

    @staticmethod
    def askInt(msg):
        inp = " "
        works = False
        while not works:
            inp = input(msg)
            try:
                inp = int(float(inp))
                works = True
            except:
                print("Invalid input: Enter an integer:") #avoid clashing with Op
        Ip.ints.append(inp)

    @staticmethod
    def getStr():
        ret = "ERROR"
        if len(Ip.strings) != 0:
            ret = Ip.strings.pop(0)
        return ret

    @staticmethod
    def getInt():
        ret = -1
        if len(Ip.ints) != 0:
            ret = Ip.ints.pop(0)
        return ret

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
