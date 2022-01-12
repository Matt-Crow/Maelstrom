"""
Active abilities are attributes a character can have that they ACTIVEly choose
to trigger on their turn.

Keep in mind that, in battle, when a Character needs to choose their active,
there are two components to consider:
1. what active do I want to use?
2. who do I want to hit with that active?
Characters make a choice of which TargetOption they wish to use, not just which
active they wish to use.
"""



from maelstrom.gameplay.events import OnHitEvent, HIT_GIVEN_EVENT, HIT_TAKEN_EVENT
from maelstrom.inputOutput.output import debug
from maelstrom.util.serialize import AbstractJsonSerialable
from maelstrom.util.random import rollPercentage
from maelstrom.dataClasses.elements import ELEMENTS
from abc import abstractmethod
import functools



"""
utility classes
"""



def dmgAtLv(lv)->int:
    return int(16.67 * (1 + lv * 0.05))


class HitType:
    """
    a HitType represents either a regular hit, a miss, or a critical hit (MHC)
    """

    def __init__(self, multiplier, message):
        self.multiplier = multiplier
        self.message = message


class TargetOption:
    """
    a TargetOption specifies who a user could potentially target using an active
    ability. For example, a melee attack allows a user to strike at a closeby
    enemy, while a ranged attack can target distant enemies

    Command design pattern
    """

    def __init__(self, active: "AbstractActive", user: "Character", targets: "List<Character>"):
        self.active = active
        self.user = user
        self.targets = targets
        self.msg = f'{active.name}->{", ".join([target.name for target in targets])}'

        # this will change when non-damaging actives are introduced
        self.totalDamage = functools.reduce(lambda total, next: total + next, [
            active.calcDamageAgainst(user, target) for target in targets
        ])

    def __str__(self)->str:
        return self.msg

    def use(self)->str:
        self.user.loseEnergy(self.active.cost) # don't call this for each target
        msgs = [self.active.resolveAgainst(self.user, target) for target in self.targets]
        return "\n".join(msgs)



"""
data classes
"""



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

    @abstractmethod
    def resolveAgainst(self, target: "Character")->str:
        pass

    def canUse(self, user: "Character")->bool:
        return self.cost <= user.energy and len(self.getTargetOptions(user)) > 0

    def getTargetOptions(self, user: "Character")->"List<TargetOption>":
        """
        don't override this one
        """
        if len(user.team.enemyTeam.getMembersRemaining()) == 0:
            return []
        return [TargetOption(self, user, targets) for targets in self.doGetTargetOptions(user)]

    @abstractmethod
    def doGetTargetOptions(self, user: "Character")->"List<List<Character>>":
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

    def resolveAgainst(self, user: "Character", target: "Character")->str:
        dmg = self.calcDamageAgainst(user, target)
        hitType = self.randomHitType(user)
        dmg = int(dmg * hitType.multiplier)

        event = OnHitEvent("Attack", user, target, self, dmg)

        target.takeDmg(dmg)

        target.fireActionListeners(HIT_TAKEN_EVENT, event)
        user.fireActionListeners(HIT_GIVEN_EVENT, event)

        return f'{hitType.message}{user.name} struck {target.name} for {dmg} damage using {self.name}!'

    def calcDamageAgainst(self, user: "Character", target: "Character")->int:
        """
        MHC is not checked here so that it doesn't mess with AI
        """

        return int(
            dmgAtLv(user.level) * self.damageMult * user.getStatValue("control") / target.getStatValue("resistance")
        )

    def randomHitType(self, user: "Character")->"HitType":
        """
        randomly chooses a HitType based on this AbstractDamagingActive's crit
        chance, miss chance, and the user's luck
        """
        hit = HitType(1.0, "") # don't put a space at the end of the message
        rng = rollPercentage(user.getStatValue("luck")) / 100

        debug(f'rolled {rng}')
        debug(f'miss requires {self.missChance}')
        debug(f'crit requires {1.0 - self.critChance}')

        if rng <= self.missChance:
            hit = HitType(self.missMult, "A glancing blow! ") # need space on end
        elif rng >= 1.0 - self.critChance:
            hit = HitType(self.critMult, "A critical hit! ") # need space on end

        return hit


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

    def doGetTargetOptions(self, user: "Character")->"List<List<Character>>":
        """
        MeleeActives can hit a single active target
        """
        return [[option] for option in getActiveTargets(user.ordinal, user.team.enemyTeam.getMembersRemaining())]

class ElementalActive(AbstractDamagingActive):
    def __init__(self, name):
        super().__init__(
            name,
            'strike an enemy for 1.75X damage',
            10,
            1.75,
            0,
            1.0,
            0,
            1.0
        )

    def copy(self):
        return ElementalActive(self.name)

    def doGetTargetOptions(self, user: "Character")->"List<List<Character>>":
        """
        ElementalActives can hit a single cleave target
        """
        return [[option] for option in getCleaveTargets(user.ordinal, user.team.enemyTeam.getMembersRemaining())]



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
