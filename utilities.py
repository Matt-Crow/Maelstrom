debug = False

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

def choose(question, options):
  """
  Returns a string
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
    Op.add(question)
    for num in range(0, len(options)):
      Op.add(str(num + 1) + ": " + names[num])
    Op.dp(False)
    
    #get their input
    Ip.askInt("Enter a number: ") # automatically checks for number
    ret = options[set_in_bounds(Ip.getInt() - 1, 0, len(options) - 1)]
    """
    the -1 is because they will enter a number from 1 to len(options),
    so I have to convert it to the corresponding index.
    set_in_bounds will make any number work
    """
  return ret

def to_list(change):
  r = []
  if type(change) == type([1, 2, 3]) or type(change) == type((1, 2, 3)):
    for item in change:
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
    if type(object) == type("string"):
      ret.append(object)
    else:
      ret.append(object.name)
  return ret

def pause():
  raw_input("Press enter/return to continue")

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
      inp = raw_input(msg)
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
  
  @classmethod
  def add(op, msg):
    msg = to_list(msg)
    for line in msg:
      op.msgs.append(line)
  
  @classmethod
  def reset(op):
    op.msgs = []

class Op(AbstractOutput):
  """
  Op is used to output most of the program
  Use Op.add(msg) to add anything to its next
  bout of output. It will automatically convert
  msg into a list
  """
  @staticmethod
  def dp(p = True):
    print('\n')
    for msg in Op.msgs:
      print(str(msg))
    Op.reset()
    if p:
      pause()

class Dp(AbstractOutput):
  @staticmethod
  def dp():
    if debug and len(Dp.msgs) is not 0:
      print('\n')
      print("<*DEBUG*>")
      for msg in Dp.msgs:
        print(str(msg))
      Dp.reset()
      pause()