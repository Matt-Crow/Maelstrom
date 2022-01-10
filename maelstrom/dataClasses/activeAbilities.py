"""
Active abilities are attributes a character can have that they ACTIVEly choose
to trigger on their turn.
"""



from maelstrom.gameplay.combat import resolveAttack
from maelstrom.inputOutput.output import debug
from util.serialize import AbstractJsonSerialable
from util.stringUtil import formatPercent
from util.utilities import ELEMENTS, roll_perc
from abc import abstractmethod



class HitType:
    def __init__(self, multiplier, message):
        self.multiplier = multiplier
        self.message = message



class AbstractActive(AbstractJsonSerialable):
    def __init__(self, name, description, cost):
        """
        name should be a unique identifier
        """
        super().__init__(type="Active")
        self.name = name
        self.description = f'{name}: {description}'
        self.cost = cost

    @abstractmethod
    def copy(self):
        pass

    def canUse(self, user: "Character", userOrdinal: int, targetTeam: "List<Character>")->bool:
        return self.cost <= user.energy and len(self.getTargetOptions(userOrdinal, targetTeam)) > 0

    def getTargetOptions(self, userOrdinal: int, targetTeam: "List<Character>")->"List<List<Character>>":
        """
        don't override this one
        """
        if len(targetTeam) == 0:
            return []
        return self.doGetTargetOptions(userOrdinal, targetTeam)

    @abstractmethod
    def doGetTargetOptions(self, userOrdinal: int, targetTeam: "List<Character>")->"List<List<Character>>":
        """
        subclasses must override this option to return the enemies this could
        potentially hit. Each element of the returned list represents a choice
        the user or AI can make, with each of those elements containing the
        enemies that attack would hit.
        """
        pass

    def toJson(self): # override default method
        return self.name

class AbstractDamagingActive(AbstractActive):
    # not sure if I like so many paramters
    def __init__(self, name, description, cost, damageMult, missChance, missMult, critChance, critMult):
        super().__init__(name, description, cost)
        self.damageMult = damageMult
        self.missChance = missChance
        self.missMult = missMult
        self.critChance = critChance
        self.critMult = critMult

    def randomHitType(self, user: "Character")->"HitType":
        """
        randomly chooses a HitType based on this AbstractDamagingActive's crit
        chance, miss chance, and the user's luck
        """
        hit = HitType(1.0, "") # don't put a space at the end of the message
        rng = roll_perc(user.getStatValue("luck")) / 100

        debug(f'rolled {rng}')
        debug(f'miss requires {self.missChance}')
        debug(f'crit requires {1.0 - self.critChance}')

        if rng <= self.missChance:
            hit = HitType(self.missMult, "A glancing blow! ") # need space on end
        elif rng >= 1.0 - self.critChance:
            hit = HitType(self.critMult, "A critical hit! ") # need space on end

        return hit

    def use(self, user: "Character", userOrdinal: int, targetTeam: "List<Character>", choice: int)->"List<str>":
        user.loseEnergy(self.cost)

        msgs = []

        targets = self.getTargetOptions(userOrdinal, targetTeam)[choice]

        for target in targets:
            msgs.append(resolveAttack((user, target, self)))

        return msgs

class MeleeActive(AbstractDamagingActive):
    # not sure if I like so many paramters
    def __init__(self, name, description, damageMult, missChance, missMult, critChance, critMult):
        super().__init__(name, description, 0, damageMult, missChance, missMult, critChance, critMult)
        self.damageMult = damageMult
        self.missChance = missChance
        self.missMult = missMult
        self.critChance = critChance
        self.critMult = critMult

    def copy(self):
        return MeleeActive(
            self.name,
            self.description,
            self.damageMult,
            self.missChance,
            self.missMult,
            self.critChance,
            self.critMult
        )

    def doGetTargetOptions(self, userOrdinal: int, targetTeam: "List<Character>")->"List<List<Character>>":
        """
        MeleeActives can hit a single active target
        """
        return [[option] for option in getActiveTargets(userOrdinal, targetTeam)]

class ElementalActive(AbstractDamagingActive):
    def __init__(self, name):
        super().__init__(
            name,
            'strike an enemy for 1.75X damage',
            5,
            1.75,
            0,
            0,
            0,
            0
        )

    def copy(self):
        return ElementalActive(self.name)

    def doGetTargetOptions(self, userOrdinal: int, targetTeam: "List<Character>")->"List<List<Character>>":
        """
        ElementalActives can hit a single cleave target
        """
        return [[option] for option in getCleaveTargets(userOrdinal, targetTeam)]



"""
Use these to decide which enemies to target. Should only allow user to choose
attacks that can hit anyone
"""


def getActiveTargets(attackerOrdinal: int, targetTeam: "List<Character>")->"List<Character>":
    """
    'active' enemies are those across from the attacker and the enemy
    immediately below that. This gives a slight advantage to the 1 in a 1 vs 2,
    as both enemies cannot attack them at the same time

    O-X
     \X
    """
    options = []
    if attackerOrdinal < len(targetTeam):
        options.append(targetTeam[attackerOrdinal])
    if attackerOrdinal + 1 < len(targetTeam):
        options.append(targetTeam[attackerOrdinal + 1])
    return options

def getCleaveTargets(attackerOrdinal: int, targetTeam: "List<Character>")->"List<Character>":
    """
    enemies are 'cleaveable' (for want of a better word) if they are no more
    than 1 array slot away from the enemy across from the attacker
     /X
    O-X
     \X
    """
    options = getActiveTargets(attackerOrdinal, targetTeam)
    if attackerOrdinal - 1 >= 0 and attackerOrdinal - 1 < len(targetTeam):
        m = targetTeam[attackerOrdinal - 1]
        options.insert(0, m)
    return options

def getDistantTargets(attackerOrdinal: int, targetTeam: "List<Character>")->"List<Character>":
    """
    the union of distant targets and cleave targets is all enemies, with no
    overlap
    """
    notTargets = getCleaveTargets(attackerOrdinal, targetTeam)
    return [member for member in targetTeam if member not in notTargets]

def testTargettingSystem():
    targetTeam = [0, 1, 2, 3]

    assert getActiveTargets(0, targetTeam) == [0, 1]
    assert getActiveTargets(1, targetTeam) == [1, 2]
    assert getActiveTargets(2, targetTeam) == [2, 3]
    assert getActiveTargets(3, targetTeam) == [3]
    assert getActiveTargets(4, targetTeam) == []

    assert getCleaveTargets(0, targetTeam) == [0, 1]
    assert getCleaveTargets(1, targetTeam) == [0, 1, 2]
    assert getCleaveTargets(2, targetTeam) == [1, 2, 3]
    assert getCleaveTargets(3, targetTeam) == [2, 3]
    assert getCleaveTargets(4, targetTeam) == [3]

    assert getDistantTargets(0, targetTeam) == [2, 3]
    assert getDistantTargets(1, targetTeam) == [3]
    assert getDistantTargets(2, targetTeam) == [0]
    assert getDistantTargets(3, targetTeam) == [0, 1]
    assert getDistantTargets(4, targetTeam) == [0, 1, 2]

    print("done testing targetting system")



def getUniversalActives()->"List<AbstractActive>":
    return [
        MeleeActive("slash", "strike a nearby enemy", 1.0, 0.2, 0.75, 0.2, 1.5),
        MeleeActive("jab", "strike a nearby enemy, with a high chance for a critical hit", 0.8, 0.1, 0.5, 0.5, 3.0),
        MeleeActive("slam", "strike recklessly at a nearby enemy", 1.5, 0.4, 0.5, 0.15, 2.0)
    ]

def getActivesForElement(element)->"List<AbstractActive>":
    return [ElementalActive(f'{element} bolt')]

def getActiveAbilityList()->"List<AbstractActive":
    options = getUniversalActives()
    for element in ELEMENTS:
        options.extend(getActivesForElement(element))
    options.extend(getActivesForElement("stone"))
    return options

def createDefaultActives(element)->"List<AbstractActive>":
    options = getUniversalActives()
    options.extend(getActivesForElement(element))
    return [option.copy() for option in options]
