"""
Active abilities are attributes a character can have that they ACTIVEly choose
to trigger on their turn.
"""



from util.serialize import AbstractJsonSerialable
from util.stringUtil import formatPercent
from util.utilities import ELEMENTS
from abc import abstractmethod



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

    def canUse(self, user: "AbstractCharacter", userOrdinal: int, targetTeam: "List<AbstractCharacter>")->bool:
        return self.cost <= user.energe and len(self.getTargets(userOrdinal, targetTeam)) > 0

    @abstractmethod
    def getTargets(self, userOrdinal: int, targetTeam: "List<AbstractCharacter>")->"List<AbstractCharacter>":
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

class MeleeActive(AbstractDamagingActive):
    # not sure if I like so many paramters
    def __init__(self, name, description, damageMult, missChance, missMult, critChance, critMult):
        super().__init__(name, description, 0, damageMult, missChance, missMult, critChance, critMult)
        self.damageMult = damageMult
        self.missChance = missChance
        self.missMult = missMult
        self.critChance = critChance
        self.critMult = critMult

    def getTargets(self, userOrdinal: int, targetTeam: "List<AbstractCharacter>")->"List<AbstractCharacter>":
        return getActiveTargets(userOrdinal, targetTeam)

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

    def getTargets(self, userOrdinal: int, targetTeam: "List<AbstractCharacter>")->"List<AbstractCharacter>":
        return getCleaveTargets(userOrdinal, targetTeam)



"""
Use these to decide which enemies to target. Should only allow user to choose
attacks that can hit anyone
"""


def getActiveTargets(attackerOrdinal: int, targetTeam: "List<AbstractCharacter>")->"List<AbstractCharacter>":
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

def getCleaveTargets(attackerOrdinal: int, targetTeam: "List<AbstractCharacter>")->"List<AbstractCharacter>":
    """
    enemies are 'cleaveable' (for want of a better word) if they are no more
    than 1 array slot away from the enemy across from the attacker
     /X
    O-X
     \X
    """
    options = getActiveTargets(attackerOrdinal, targetTeam)
    if attackerOrdinal - 1 >= 0:
        options.insert(0, targetTeam[attackerOrdinal - 1])
    return options

def getDistantTargets(attackerOrdinal: int, targetTeam: "List<AbstractCharacter>")->"List<AbstractCharacter>":
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



def getActiveAbilityList()->"List<AbstractActive":
    options =  [
        MeleeActive("slash", "strike a nearby enemy", 1.0, 0.2, 0.75, 0.2, 1.5),
        MeleeActive("jab", "strike a nearby enemy, with a high chance for a critical hit", 0.8, 0.1, 0.5, 0.5, 3.0),
        MeleeActive("slam", "strike recklessly at a nearby enemy", 1.5, 0.4, 0.5, 0.15, 2.0)
    ]
    options.extend([ElementalActive(f'{element} bolt') for element in ELEMENTS])
    return options
