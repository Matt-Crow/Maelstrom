debug = True

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
    Dp.add(str(num) + " is too low")
    ret = min
  elif num > max:
    Dp.add(str(num) + " is too high")
    ret = max
  Dp.dp()
  return ret

#still working on, convert to string elsewhere
def choose(question, options):
  ret = False
  options = to_list(options)
  if len(options) == 1:
    ret = options[0]
  else:
    print(question)
    
    for option in range(0, len(options)):
      print(str(num + 1) + ": " + options[option])
    
    answered = False
    
    while not answered:
      choice = raw_input(" ")
      for option in options:
        try:
          compare = option.name.lower()
        except:
          compare = option.lower()
        
        if choice.lower() == compare:
          return option
        elif choice == str(options.index(option) + 1):
          return option
      print("That isn't an option...")

  return ret

def to_list(change):
  r = []
  if type(change) == type([1, 2, 3]) or type(change) == type((1, 2, 3)):
    for item in change:
      r.append(item)
  else:
    r.append(change)
  return r

class Ip:
  """
  Input
  """
  strings = []
  ints = []
  
  @staticmethod
  askStr(msg):
    Ip.strings.append(raw_input(msg))

  @staticmethod
  askInt(msg):
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
  getStr():
    ret = "ERROR"
    if len(Ip.strings) != 0:
      ret = Ip.strings.pop(0)
    return ret
  
  @staticmethod
  getInt():
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
  def dp():
    print('\n')
    for msg in Op.msgs:
      print(str(msg))
    Op.reset()

class Dp(AbstractOutput):
  @staticmethod
  def dp():
    if debug and len(Dp.msgs) is not 0:
      print('\n')
      print("<*DEBUG*>")
      for msg in Dp.msgs:
        print(str(msg))
      Dp.reset()