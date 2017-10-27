debug = False

def mod(num):
  """
  A useful little guy
  """
  if num < 1:
    num = 1
  return num

def set_in_bounds(num, min, max):
  if num < min:
    dp(str(num) + " is too low")
    return min
  elif num > max:
    dp(str(num) + " is too high")
    return max
  else:
    return num

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

class Op:
  """
  Op is used to output most of the program
  Use Op.add(msg) to add anything to its next
  bout of output. It will automatically convert
  msg into a list
  """
  msgs = []
  
  @staticmethod
  def add(msg):
    msg = to_list(msg)
    for line in msg:
      Op.msgs.append(line)
  
  @staticmethod
  def reset():
    Op.msgs = []
  
  @staticmethod
  def dp():
    print('\n')
    for msg in Op.msgs:
      print(str(msg))
    Op.reset()

# debug print
def dp(write):
  if not debug:
    return
  list = []
  if type(write) != type([0, 0, 0, 0]):
    list.append(write)
  else:
    list = write
  print " "
  print("<*DEBUG*>")
  for item in list:
    print item
  print " "