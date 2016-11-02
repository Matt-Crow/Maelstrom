from maelstrom_classes import *
import random

do_MHC = True
debug = True


# This is ugly
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


lightning = Element("Lightning", "Wind")
wind = Element("Wind", "Hail")
hail = Element("Hail", "Rain")
rain = Element("Rain", "Lightning")
stone = Element ("Stone", None)

# use these in specials
no_MHC = (0, -1)
no_MHC_mult = (1, 1)
no_eff = (0, 0, 0)
act_ene = ("enemy", "act")

boom = Attack(("BOOM!", 9999, no_MHC, no_MHC_mult, ("enemy", "all"), no_eff))
LAct = Attack(("Shock Pulse", 1.7, no_MHC, no_MHC_mult, act_ene, no_eff))
RAct = Attack(("Water Pulse", 1.7, no_MHC, no_MHC_mult, act_ene, no_eff))
HAct = Attack(("Icicle Pulse", 1.7, no_MHC, no_MHC_mult, act_ene, no_eff))
WAct = Attack(("Vacuum Pulse", 1.7, no_MHC, no_MHC_mult, act_ene, no_eff))
LAll = Attack(("Shock Wave", 0.67, no_MHC, no_MHC_mult, ("enemy", "all"), no_eff))
RAll = Attack(("Tidal Wave", 0.67, no_MHC, no_MHC_mult, ("enemy", "all"), no_eff))
HAll = Attack(("Avalanche", 0.67, no_MHC, no_MHC_mult, ("enemy", "all"), no_eff))
WAll = Attack(("Tempest", 0.67, no_MHC, no_MHC_mult, ("enemy", "all"), no_eff))
LAny = Attack(("Thunderbolt", 0.8, no_MHC, no_MHC_mult, ("enemy", "any"), no_eff))
RAny = Attack(("Water bolt", 0.8, no_MHC, no_MHC_mult, ("enemy", "any"), no_eff))
HAny = Attack(("Frost bolt", 0.8, no_MHC, no_MHC_mult, ("enemy", "any"), no_eff))
WAny = Attack(("Wind bolt", 0.8, no_MHC, no_MHC_mult, ("enemy", "any"), no_eff))


l_start = ("Alexandre", (0, 1, 1), lightning, LAct)
r_start = ("Rene", (0, -1, 1), rain, RAct)
h_start = ("Ian", (0, -1, -1), hail, HAct)
w_start = ("Viktor", (0, 1, -1), wind, WAct)

l_all = ("Isaac", (0, 0, 0), lightning, LAll)
r_all = ("Barry", (+1, -1, +1), rain, RAll)
h_all = ("Nicole", (0, 0, 0), hail, HAll)
w_all = ("Colin", (0, -1, 0), wind, WAll)

l_any = ("Adrian", (0, 0, 0), lightning, LAny)
r_any = ("Omar", (-1, 0, -2), rain, RAny)
h_any = ("Richard", (0, 0, 0), hail, HAny)
w_any = ("Tobias", (0, -2, -1), wind, WAny)

test = ("TEST", (0, 0, 0), stone, RAct)
max = ("MAX", (5, 0, 0), stone, HAct)
min = ("MIN", (-5, 0, 0), stone, HAct)

test_team = Team("test team", (r_all, w_all, r_any))
enemy_team = Team("enemy team", (max, min, w_any))

test_fight = Battle(1, [weathers[9]])
test_fight.load_team(test_team)
test_fight.load_team(enemy_team)
test_fight.play()
