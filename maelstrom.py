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
1/11/2017 - 8/11/2017: Revised how attacks work, added hit principle
9/11/2017 - 15/11/2017 : Finished Attack, added events
17/11/2017 - 25/11/2017: Added customization, worked on save codes
26/11/2017 - 28/11/2017: Worked on Item
30/11/2017 - ? : Improved Area, Levels, and Files

Version 0.9
"""

from utilities import *
from maelstrom_classes import *
from navigate import *
from item import *
from file import *
import random

# use these in specials
no_eff = (0, 0, 0)
act_ene = ("enemy", "act")

boom = AllAttack("BOOM!", 7, 7)

LAct = ActAttack("Shock Pulse", 1.75, 5)
SAct = ActAttack("Rock Slide", 1.75, 5)

enemies["MAX"] = ((5, 0, 0, 0, 0), "stone", SAct)
enemies["MIN"] = ((-5, 0, 0, 0, 0), "stone", SAct)

enemies["Lightning Entity"] = ((-3, 3, 3, 0, 0), "lightning", SAct)
enemies["Rain Entity"] = ((3, -3, 3, 0, 0), "rain", SAct)
enemies["Hail Entity"] = ((3, -3, -3, 0, 0), "hail", SAct)
enemies["Wind Entity"] = ((-3, 3, -3, 0, 0), "wind", SAct)

enemies["stone soldier"] = ((2, -3, -3, 0, 0), "stone", SAct)

c1 = Battle("Stone Rising", EnemyTeam("Stone", {"name": "stone soldier", "level": 1}), None)
caves = Location("Ancient library caverns", "These caves seem as old as time itself.", ("LIBRARIAN: These caves have only recently by our scholars.", "Everything here is estimated to be ancient,", "perhaps even older than Altostromia itself!", "But what concerns me are these statues...", "...hundreds of them."))
lib_cav = Area("Ancient caverns", "?", caves, c1)

if __name__ == "__main__":
    #player = load()
    player = PlayerTeam("Player team", {"name": "Alexandre", "data": ((0, 0, 0, 0, 0), "lightning", LAct), "level": 1})
    player.obtain(t1)
    player.obtain(t2)
    player.obtain(t3)
    lib_cav.display_data(player)
    
    #Savefile("player_data.txt").update(player)