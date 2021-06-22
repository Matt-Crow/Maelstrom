yourDamageReceived = 0
enemyDamageReceived = 0

enemyHP = 23
enemyStr = 5
enemyWeaponGrade = 5
enemyArm = 3
enemyArmorGrade = 3
enemyAttackUsed = "Slash"

yourHP = 24
yourStr = 4
yourWeaponGrade = 4
yourArm = 4
yourArmorGrade = 4

#Time to dish out the pain!
def calcDamage(s, w, o, r, d):
    #str, weapon, arm, grade, damage
    return (w * s / 10) - (r * o / 10) + d
#Done, but needs to be more complicated :/



#Enemy attacks you! Work here
yourDamageReceived = calcDamage(enemyStr, enemyWeaponGrade, yourArm, yourArmorGrade, 3)
print "Enemy struck you for " + str(yourDamageReceived) + " damage with " + str(enemyAttackUsed) + "!"
yourHP = yourHP - yourDamageReceived
#End enemy attacking phase



#This is the part where you start attacking the opponent
def chooseAttack():
    attack = raw_input("What do you do?")
    if attack == "Slash":
        return "Slash"
    elif attack == "Jab":
        return "Jab"
    elif attack == "Slam":
        return "Slam"
    else:
        print "Erm... I'm pretty certain that that isn't an attack."

attackChosen = chooseAttack()
if attackChosen == "Slash":
    enemyDamageReceived = calcDamage(yourStr, yourWeaponGrade, enemyArm, enemyArmorGrade, 3)
elif attackChosen == "Jab":
    enemyDamageReceived = calcDamage(yourStr, yourWeaponGrade, enemyArm, enemyArmorGrade, 2)
elif attackChosen == "Slam":
    enemyDamageReceived = calcDamage(yourStr, yourWeaponGrade, enemyArm, enemyArmorGrade, 4)
else:
    attackChosen = chooseAttack()

print "You struck enemy for " + str(enemyDamageReceived) + " damage with " + str(attackChosen) + "!"
enemyHP = enemyHP - enemyDamageReceived

print enemyHP
#Finish attacking opponent