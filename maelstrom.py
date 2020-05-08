"""
Copyright (c) 2015 Matt Crow
"""

"""
Started October 28, 2015
dd/mm/yyyy
28/10/2015-: Built Attack, Warrior (later renamed Character), and Team
Week 2: Revised/improved/reordered functions
23/11/2015 - 27/11/2015: Implemented Battle
30/11/2015 - 4/12/2015: Finished most of PvP
7/12/2015 - 11/12/2015: Implemented Weather, redid stat boosts
14/12/2015 - 18/12/2015: Added data files
31/12/2015 - 1/1/2016: Worked on Special file reading

18/10/2016 - 22/10/2016: General cleanup/improvement
31/10/2016 - 6/10/2016: File work
14/11/2016 - 20/11/2016: Area and general cleanup
21/11/2016 - 1/12/2016: Added AI

6/3/2017 Started major revamp
29/3/2017 Energy is now per character as opposed to team
5/4/2017 finished going through character. Will add new features
8/4/2017 finsihed Team
11/4/2017 how_many added, need to implement
13/4/2017 fixed Contract
16/4/2017 - 23/4/2017: Started work on Weapon
24/4/2017 30/4/2107 : Added Passives
1/5/2017 : Added Location, began work on splitting file

27/10/2017: Revised output
1/11/2017 - 8/11/2017: Revised how actives work, added hit principle
9/11/2017 - 15/11/2017 : Finished Attack, added events
17/11/2017 - 25/11/2017: Added customization, worked on save codes
26/11/2017 - 28/11/2017: Worked on Item
30/11/2017 - 7/12/2017 : Improved Area, Levels, Weather, and Files
9/12/2017 - 11/12/2017 : Split files, working on campagne
12/12/2017: Working on save file
May 2020: Working on lots of cleanup and redoing serialization

Version 0.9
"""

#having stuff above the import statements is usually not good, but this cleans up my import statements
from util.path import add_subdir

add_subdir("battle")
add_subdir("util")
add_subdir("characters")

from game import Game

if __name__ == "__main__":
    input("Calling test from Maelstrom.py")
    Game().test()
    #Game().run()
