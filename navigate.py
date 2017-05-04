if __name__ == "__main__":
  print("Oops! You're running from the wrong file!")
  print("Try running Maelstrom.py instead!")
  exit()

from maelstrom_classes import to_list, op, dp, choose

class Story:
  def __init__(self, story):
    self.story = to_list(story)
  
  def print_story(self):
    for script in self.story:
      op(script)
      go = raw_input("Press enter/return to continue")

class Location:
  def __init__(self, name, desc, script):
    self.name = name
    self.description = desc
    self.script = Story(script)
    
  def display_data(self):
    op([self.name, self.description])
  
  def travel_to(self, player):
    self.script.print_story()
    self.action(player)

class Tavern(Location):
  def action(self, player):
    contracts = to_list(player.contracts)
    msg = ["So, you wan't to hire out another warrior, eh?", "Now let me see..."]
    if len(contracts) == 0:
      msg.append("Sorry, but it looks like you don't have any contracts.")
      msg.append("Come back when you have one, and then we'll talk.")
      op(msg)
      return
    msg.append("Well well well, and here I thought you weren't credibly.")
    msg.append("How about you take a look at who we got here?")
    op(msg)
    con = choose("Which contract do you want to use?", contracts)
    player.add_member(con.use())

class Area:
  def __init__(self, name, description, locations, levels):
    self.name = name
    self.description = description
    self.locations = to_list(locations)
    self.levels = to_list(levels)
        
  def display_data(self, player):
    op([self.name, self.description])
    for loc in self.locations:
      loc.display_data()
    for level in self.levels:
      level.display_data()
      
    self.trav_or_play(player)
  
  def trav_or_play(self, player):
    choice = choose("Do you wish to travel to a location, or play a level?", ("Location", "Level"))
    if choice == "Level":
      level_to_play = choose("Which level do you want to play?", self.levels)
      level_to_play.load_team(player)
      level_to_play.play()
      
    else:
      place_to_go = choose("Where do you want to go?", self.locations)
      place_to_go.travel_to(player)
    #unhash this to make it never end
    self.display_data(player)
