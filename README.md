
# Maelstrom
This is my first "mega program", as call it: The first programming project I've
poured countless hours of work into. I learned so much while making this game,
both about programming and game design in general.

TODO:
* migrate over to """maelstrom""" folder
* use my application directory system from ARCDHWebAutomator
* make the game fun
* I might want to replace the current method of serializing in-class with the
  Visitor design pattern using Python's JSONEncoder. The current method may
  break the suggestion of one purpose per class, but it's elegant compared to
  the alternative
* random campaign generator: Have the program chop up a Shakespere play and make
  characters and locations based off of that?



* do away with "Customization Points" system. Change to allow player to choose
  from sets of pre-generated content. Add "guidebooks" the player can use to
  look up info on enemies, actives, passives, and items to avoid info-dumping
  before every battle
    * de-tangle attack choosing in combat.py, character.py, and
      activeAbilities.py
    * migrate AI from EnemyCharacter and EnemyTeam to elsewhere
    * redo item equipping choice system
    
    * merge together AbstractTeam, PlayerTeam, and EnemyTeam
