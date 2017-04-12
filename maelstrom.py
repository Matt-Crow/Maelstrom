from maelstrom_classes import *
import random

do_MHC = True
debug = not True

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

boom = Attack("BOOM!", 9999, ("enemy", "all"), no_eff, 7)

LAct = Attack("Shock Pulse", 1.75, act_ene, no_eff, 5)
RAct = Attack("Water Pulse", 1.75, act_ene, no_eff, 5)
HAct = Attack("Icicle Pulse", 1.75, act_ene, no_eff, 5)
WAct = Attack("Vacuum Pulse", 1.75, act_ene, no_eff, 5)
SAct = Attack("Rock Slide", 1.75, act_ene, no_eff, 5)

LAll = Attack("Shock Wave", 0.67, ("enemy", "all"), no_eff, 5)
RAll = Attack("Tidal Wave", 0.67, ("enemy", "all"), no_eff, 5)
HAll = Attack("Avalanche", 0.67, ("enemy", "all"), no_eff, 5)
WAll = Attack("Tempest", 0.67, ("enemy", "all"), no_eff, 5)

LAny = Attack("Thunderbolt", 1.25, ("enemy", "any"), no_eff, 5)
RAny = Attack("Water bolt", 1.25, ("enemy", "any"), no_eff, 5)
HAny = Attack("Frost bolt", 1.25, ("enemy", "any"), no_eff, 5)
WAny = Attack("Wind bolt", 1.25, ("enemy", "any"), no_eff, 5)

characters["TEST"] = ((0, 0, 0), "stone", SAct)
characters["Alexandre"] = ((0, 1, 1), "lightning", LAct)
characters["Rene"] = ((0, -1, 1), "rain", RAct)
characters["Ian"] = ((0, -1, -1), "hail", HAct)
characters["Viktor"] = ((0, 1, -1), "wind", WAct)

characters["Isaac"] = ((-1, 0, -3), "lightning", LAll)
characters["Barry"] = ((1, -1, 1), "rain", RAll)
characters["Nicole"] = ((1, 2, 2), "hail", HAll)
characters["Colin"] = ((0, -1, 0), "wind", WAll)

characters["Adrian"] = ((1, -2, 1), "lightning", LAny)
characters["Omar"] = ((-1, 0, -2), "rain", RAny)
characters["Richard"] = ((-1, -3, -3), "hail", HAny)
characters["Tobias"] = ((0, -2, -1), "wind", WAny)

enemies["MAX"] = ((5, 0, 0), "stone", SAct)
enemies["MIN"] = ((-5, 0, 0), "stone", SAct)

enemies["Lightning Entity"] = ((-3, 3, 3), "lightning", LAct)
enemies["Rain Entity"] = ((3, -3, 3), "rain", RAct)
enemies["Hail Entity"] = ((3, -3, -3), "hail", HAct)
enemies["Wind Entity"] = ((-3, 3, -3), "wind", WAct)

if __name__ == "__main__":
    #player = load()
    player = Team("Player team", (("Alexandre", 1)), False)
    
    """    
    # temporary
    t = Tavern("The salty spitoon")
    c = Contract(None)
    cc = Contract("Alexandre")
    t.recruit(player, (c, cc))
    """
    r1 = Battle("Origin Beaches", "All heroes have to start somewhere", ("Encounter! Rain Entity", "Quick! Knock its hit points down to zero and escape!"), ("Congradulations!", "The Entity dissipates into a cloud of smoke"), 1, None)
    r1.load_team(Team("Rain", (("Rain Entity", 1)), True))
    r2 = Battle("The Gravel Trail", "A rough path leads up from the beaches...", ("The gravel crunches beneath your feet as you walk", "Suddenly it starts to drizzle lightly", "TIP: While it is raining, all characters will regain a little HP each turn"), ("Congradulations!"), 1, weathers[9])
    r2.load_team(Team("Rain", (("Rain Entity", 1)), True))
    r3 = Battle("The Stagnant Pools", "Alongside the path lie many puddles...", ("A puddle begins to ripple...", "...and take form!", "TIP: Higher level characters have better stats, but HP grows slowly"), ("Congradulations!", "Perhaps an ally will help you in your quest..."), 1, weathers[10])
    r3.load_team(Team("Rain", (("Rain Entity", 2)), True))
    rain_village = Area("The Rain Village", "Where peace and tranquility hang over like a fine mist", (r1, r2, r3))
    rain_village.display_data(player)
    
    h1 = Battle("Forest Clearing", "A fresh coating of snow covers all the trees", None, None, 1, weathers[6])
    h1.load_team(Team(" ", (("Hail Entity", 1)), True))
    hail_village = Area("The Hail Village", "?", (h1))
    #hail_village.display_data(player)
    
    #m.update(player_team)