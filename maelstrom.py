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
17/11/2017 - ?: Added customization

Version 0.9
"""

from utilities import *
from maelstrom_classes import *
from navigate import *
import random

weathers = (
  Weather("Lightning", 40.0, "Flashes of light can be seen in the distance..."),
  Weather("Lightning", 50.0, "Thunder rings not far away..."),
  Weather("Lightning", 60.0, "The sky rains down its fire upon the field..."),
  
  Weather("Wind", 40.0, "A gentle breeze whips through..."),
  Weather("Wind", 50.0, "The strong winds blow mightily..."),
  Weather("Wind", 60.0, "A twister rips up the land..."),
  
  Weather("Hail", 2.5, "A light snow was falling..."),
  Weather("Hail", 5, "Hail clatters along the ground..."),
  Weather("Hail", 7.5, "The field is battered by hail..."),
  
  Weather("Rain", 2.5, "A light rain falls..."),
  Weather("Rain", 5, "A brisk shower is forecast..."),
  Weather("Rain", 7.5, "A deluge of water pours forth from the sky...")
  )

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

# move messages to seperate file
"""
r1 = Battle("Origin Beaches", "All heroes have to start somewhere", ("Encounter! Rain Entity", "Quick! Knock its hit points down to zero and escape!"), ("Congradulations!", "The Entity dissipates into a cloud of smoke"), 1, None)
r1.load_team(Team("Rain", {"name":"Rain Entity", "level": 1}, True))
r2 = Battle("The Gravel Trail", "A rough path leads up from the beaches...", ("The gravel crunches beneath your feet as you walk", "Suddenly it starts to drizzle lightly", "TIP: While it is raining, all characters will regain a little HP each turn"), ("Congradulations!"), 1, weathers[9], None)
r2.load_team(Team("Rain", {"name": "Rain Entity", "level": 1}, True))
r3 = Battle("The Stagnant Pools", "Alongside the path lie many puddles...", ("A puddle begins to ripple...", "...and take form!", "TIP: Higher level characters have better stats, but HP grows slowly"), ("Congradulations!", "Perhaps an ally will help you in your quest..."), 1, weathers[10], None)
r3.load_team(Team("Rain", {"name": "Rain Entity", "level": 2}, True))
r4 = Battle("Deluge", "The rain begins to pour...", ("Flashes of lightning...", "...no longer distant!"), ("You are far stronger than you appear..."), 4, (weathers[0], weathers[1], weathers[2]), None)
r4.load_team(Team("Rain", ({"name": "Lightning Entity", "level": 1}, {"name": "Rain Entity", "level": 1}, {"name": "Hail Entity", "level": 1}, {"name": "Wind Entity", "level": 1}), True))
t = Tavern("The Salty Spitoon", "Welcome to the Salty Spitoon, how tough are you?", ["How tough am I?", "I programmed a chessboard the other day!", "Yeah, so?", "...recursively.", "Ugh, come right this way, sorry to keep you waiting."])
rain_village = Area("The Rain Village", "Where peace and tranquility hang over like a fine mist", t, (r1, r2, r3, r4))

h1 = Battle("Forest Clearing", "A fresh coating of snow covers all the trees", None, None, 1, weathers[6], None)
h1.load_team(Team(" ", {"name": "Hail Entity", "level": 1}, True))
hail_village = Area("The Hail Village", "?", None, (h1))
"""
c1 = Battle("Stone Rising", "An ancient threat arises", ("STONE SOLDIER: Foolish ones seek to take our land", "when we ourselves are imbued with its very power!"), "The stone soldier shatters into dust.", 1, None)
c1.load_team(EnemyTeam("Stone", {"name": "stone soldier", "level": 1}))
caves = Location("Ancient library caverns", "These caves seem as old as time itself.", ("LIBRARIAN: These caves have only recently by our scholars.", "Everything here is estimated to be ancient,", "perhaps even older than Altostromia itself!", "But what concerns me are these statues...", "...hundreds of them."))
lib_cav = Area("Ancient caverns", "?", caves, c1)

if __name__ == "__main__":
  #player = load()
  player = PlayerTeam("Player team", {"name": "Alexandre", "data": ((0, 0, 0, 0, 0), "lightning", LAct), "level": 1})
  
  lib_cav.display_data(player)
  #Savefile("player_data.txt").update(player)