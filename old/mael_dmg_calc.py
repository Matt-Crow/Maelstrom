TOTAL = 1000

def calc_stats(defRat, eleRat, resRat, p = True):
	DEF = TOTAL * (0.75 + 0.025 * defRat)
	OFF = TOTAL - DEF
	
	ENE = OFF * (0.5 + 0.05 * eleRat)
	STR = OFF - ENE
	
	RES = DEF * (0.167 + 0.033 * resRat)
	HP = DEF - RES
	
	if p:
		print ""
		print ""
		print "HP: " + str(HP)
		print "STR: " + str(STR)
		print "ENE: " + str(ENE)
		print "RES: " + str(RES)
	
		print ""
		print ""
	
	else:
		return (HP, STR, ENE, RES)

def calc_dmg(attacker_stats, defender_stats):
	HP = defender_stats[0]
	STR = attacker_stats[1]
	ENE = attacker_stats[2]
	RES = defender_stats[3]
	
	adv = raw_input("What is the attacker's advantage status? (s/n/w)")
	if adv == "s":
		FLOOR = 1.115
		
	elif adv == "w":
		FLOOR = 0.625
		
	else:
		FLOOR = 0.85
		
	CEILING = FLOOR * 1.5
	
	ele_dmg = ENE / RES
	
	if ele_dmg > CEILING:
		ele_dmg = CEILING
		
	elif ele_dmg < FLOOR:
		ele_dmg = CEILING
	
	dmg = STR * ele_dmg
	
	print str(dmg) + " damage: " + str(dmg / HP * 100) + "%" 
	
	

def ask_stats(p):
	DR = raw_input("Choose defRat (3 to -3)")
	ER = raw_input("Choose eleRat (3 to -3)")
	RR = raw_input("Choose resRat (3 to -3)")
		
	return calc_stats(int(DR), int(ER), int(RR), p)


	
def ask():
	print "What do you want me to calculate?"
	print "(s) Stats"
	print "(d) Damage"
	choice = raw_input("")
	
	if choice.lower() == "s":
		print "Stats coming right up!"
		ask_stats(True)
		print "There you go!"
		
		more = raw_input("Do you need anything else? (y/n)")
		if more == "y":
			ask()
			
		else:
			print "Glad I could be of assistance."
	
	elif choice.lower() == "d":
		calc_dmg(ask_stats(False), ask_stats(False))
		
		more = raw_input("Do you need anything else? (y/n)")
		if more == "y":
			ask()
			
		else:
			print "Glad I could be of assistance."
	
	else:
		print "I'm afraid I don't understand..."
		ask()
		
		
ask()