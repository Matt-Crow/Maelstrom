
# Maelstrom
This is my first "mega program", as call it: The first programming project I've
poured countless hours of work into. I learned so much while making this game,
both about programming and game design in general.

## Running the Program
First, run using """python maelstrom.py -s""" to store the data used by the
program. After that, you can run using """python maelstrom.py""".

Use """python maelstrom.py -h""" to view command line options.

## Testing
`python -m unittest`

TODO:
* use my application directory system from ARCDHWebAutomator
* controller system a la maelstrom/gameplay/levelController.py
* make the game fun
* I might want to replace the current method of serializing in-class with the
  Visitor design pattern using Python's JSONEncoder. The current method may
  break the suggestion of one purpose per class, but it's elegant compared to
  the alternative
* random campaign generator: Have the program chop up a Shakespere play and make
  characters and locations based off of that?
* Replacement for Customization Points system:
    * replace Items with a new "stat DNA block" class that provides minor
      bonuses to stats
    * a level X character can have up to X stat DNA blocks equipped
    * redo item equipping choice system
* Add "guidebooks" the player can use to look up info on enemies, actives,
  passives, and items to avoid info-dumping before every battle
