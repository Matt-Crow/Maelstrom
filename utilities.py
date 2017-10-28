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

def choose(question, options):
  if len(options) == 1:
    return options[0]
  
  print(question)
  
  num = 1
  for option in options:
    try:
      name = option.name  
    except:
      name = option
    
    print(str(num) + ": " + name)  
    num += 1
  
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

def to_list(change):
  r = []
  if type(change) == type([1, 2, 3]) or type(change) == type((1, 2, 3)):
    for item in change:
      r.append(item)
  else:
    r.append(change)
  return r

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