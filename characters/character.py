from utilities import choose, ELEMENTS, STATS, Dp
from stat_classes import Stat
from characters.actives.actives import AbstractActive
from passives import AbstractPassive
from item import Item
from events import OnHitEvent, ActionRegister, HIT_GIVEN_EVENT, HIT_TAKEN_EVENT, UPDATE_EVENT
from customizable import AbstractCustomizable
from util.output import Op
from fileSystem import saveSerializable, loadSerializable, ENEMY_DIR
from util.stringUtil import entab

"""
Characters
"""

"""
A Class containing all the info for a character
May move the inheritance from AbstractCustomizable up to PlayerCharacter,
and make this instead inherit from AbstractJsonSerialable
"""
class AbstractCharacter(AbstractCustomizable):
    """
    Initializers:
    Used to 'build' the characters

    required kwargs:
    - type : str
    - name : str
    - customizationPoints : int (defaults to 0)
    - element : str
    - level : int (defaults to 1)
    - xp : int (defaults to 0)
    - actives : list (defaults to AbstractActive.getDefaults(element))
    - passives : list (default to AbstractPassive.getDefaults())
    - equippedItems : list (defaults to Item.getDefaults())
    - stats: object{ str : int } (defaults to 0 for each stat in STATS not given in the object)
    """
    def __init__(self, **kwargs):
        super(AbstractCharacter, self).__init__(**kwargs)
        self.maxHp = 100

        self.element = kwargs["element"]
        self.level = kwargs.get("level", 1)
        self.xp = kwargs.get("xp", 0)

        self.actives = []
        self.passives = []
        self.equippedItems = []
        for active in kwargs.get("actives", AbstractActive.getDefaults(self.element)):
            self.addActive(active)
        for passive in kwargs.get("passives", AbstractPassive.getDefaults()):
            self.addPassive(passive)
        for item in kwargs.get("equippedItems", Item.getDefaults()):
            self.equipItem(item)

        for stat in STATS:
            self.addStat(Stat(stat, lambda base: 20.0 + float(base), kwargs.get("stats", {}).get(stat, 0)))
        self.calcStats()
        self.remHp = self.maxHp

        self.actionRegister = ActionRegister()

        self.addSerializedAttributes(
            "element",
            "xp",
            "level",
            "actives",
            "passives",
            "equippedItems"
        )

    """
    The new default method.
    """
    @staticmethod
    def createDefaultPlayer(name="Name not set", element=ELEMENTS[0])->"PlayerCharacter":
        player = PlayerCharacter(
            name=name,
            element=element
        )
        return player

    """
    Returns a deep copy of this character
    """
    def copy(self)->"AbstractCharacter":
        return AbstractCharacter.deserializeJson(self.toJsonDict())

    """
    Reads a JSON object as a dictionary, then converts it to an AbstractCharacter
    """
    @classmethod
    def deserializeJson(cls, jdict: dict)->"AbstractCharacter":
        ctype = jdict["type"]
        jdict["actives"] = [AbstractActive.deserializeJson(data) for data in jdict["actives"]]
        jdict["passives"]= [AbstractPassive.deserializeJson(data) for data in jdict["passives"]]
        jdict["equippedItems"] = [Item.deserializeJson(data) for data in jdict["equippedItems"]]
        ret = None

        if ctype == "PlayerCharacter":
            ret = PlayerCharacter(**jdict)
        elif ctype == "EnemyCharacter":
            ret = EnemyCharacter(**jdict)
        else:
            raise Exception("Type not found! " + ctype)

        return ret

    def addActive(self, active: "AbstractActive"):
        self.actives.append(active)
        active.setUser(self)
        active.calcStats()

    def addPassive(self, passive: "AbstractPassive"):
        self.passives.append(passive)
        passive.setUser(self)
        passive.calcStats()

    def equipItem(self, item: "Item"):
        self.equippedItems.append(item)
        item.setUser(self)
        item.equip(self)
        item.calcStats()

    # HP defined here
    def initForBattle(self):
        self.actionRegister.clear()
        self.calcStats()

        for active in self.actives:
            active.setUser(self)
            active.initForBattle()

        for passive in self.passives:
            passive.setUser(self)
            passive.initForBattle()

        for item in self.equippedItems:
            item.setUser(self)
            item.applyBoost()

        self.remHp = self.maxHp
        self.energy = int(self.getStatValue("energy") / 2.0)

    def addActionListener(self, enumType, action):
        self.actionRegister.addActionListener(enumType, action)
    def fireActionListeners(self, enumType, event=None):
        self.actionRegister.fire(enumType, event)

    """
    Returns as a value between 0 and 100
    """
    def getHpPerc(self):
        return int((float(self.remHp) / float(self.maxHp) * 100.0))

    def getDisplayData(self)->str:
        self.calcStats()
        ret = [
            f'{self.name} Lv. {self.level} {self.element}',
            entab(f'{self.xp} / {self.level * 10} XP')
        ]

        ret.append("STATS:")
        for stat in STATS:
            ret.append(entab(f'{stat}: {int(self.getStatValue(stat))}'))

        ret.append("ACTIVES:")
        for active in self.actives:
            ret.append(entab(active.getDisplayData()))

        ret.append("PASSIVES:")
        for passive in self.passives:
            ret.append(entab(passive.getDisplayData()))

        ret.append("ITEMS:")
        for item in self.equippedItems:
            ret.append(entab(item.getDisplayData()))

        return "\n".join(ret)

    """
    Battle functions:
    Used during battle
    """
    # add ID checking to prevent doubling up
    def boost(self, boost):
        """
        Increase or lower stats in battle
        amount will be an integeral amount
        20 translates to 20%
        """
        mult = 1 + self.getStatValue("potency") / 100
        self.stats[boost.stat_name].boost(boost)

    """
    Restores HP.
    Converts an INTEGER
    to a percentage.
    """
    def heal(self, percent):
        mult = 1 + self.getStatValue("potency") / 100
        healing = self.maxHp * (float(percent) / 100)
        self.remHp = self.remHp + healing * mult

        Op.add(self.name + " healed " + str(int(healing)) + " HP!")
        Op.display()

        if self.remHp > self.maxHp:
            self.remHp = self.maxHp

    def harm(self, percent):
        mult = 1 - self.getStatValue("potency") / 100
        harming = self.maxHp * (float(percent) / 100)
        self.takeDmg(harming * mult)
        Op.add(self.name + " took " + str(int(harming * mult)) + " damage!")
        Op.display()

    def takeDmg(self, dmg):
        self.remHp -= dmg
        self.remHp = int(self.remHp)
        self.team.updateMembersRem()

    def gainEnergy(self, amount):
        self.energy += amount

        if self.energy > self.getStatValue("energy"):
            self.energy = self.getStatValue("energy")

        self.energy = int(self.energy)

    def loseEnergy(self, amount):
        self.energy -= amount
        if self.energy < 0:
            self.energy = 0

    def update(self):
        self.fireActionListeners(UPDATE_EVENT, self)
        self.gainEnergy(self.getStatValue("energy") * 0.15)
        for stat in self.stats.values():
            stat.update()

    """
    Damage calculation
    """
    def calcDmgTaken(self, attacker, activeUsed):
        """
        MHC is not checked here so that it doesn't
        mess with AI
        """
        damage = activeUsed.damage * attacker.getStatValue("control") / self.getStatValue("resistance")

        if attacker.team.switched_in:
            damage = damage * 0.75

        return damage

    def struckBy(self, attacker, activeUsed):
        dmg = self.calcDmgTaken(attacker, activeUsed)
        dmg = dmg * activeUsed.getMHCMult()
        Op.add(attacker.name + " struck " + self.name)
        Op.add("for " + str(int(dmg)) + " damage")
        Op.add("using " + activeUsed.name + "!")
        Op.display()

        event = OnHitEvent("Attack", attacker, self, activeUsed, dmg)
        event.displayData()

        self.fireActionListeners(HIT_TAKEN_EVENT, event)
        attacker.fireActionListeners(HIT_GIVEN_EVENT, event)
        self.takeDmg(dmg)

    def isKoed(self):
        return self.remHp <= 0



"""
A PlayerCharacter is a Character controlled by a player.
Currently, each player has only one character, but I will
leave that open to adjustment
"""
class PlayerCharacter(AbstractCharacter):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**dict(kwargs, type="PlayerCharacter"))

    def chooseActive(self):
        options = []
        for active in self.actives:
            if active.canUse():
                options.append(active)

        choose("What active do you wish to use?", options).use()

    """
    Post-battle actions:
    Occur after battle
    """
    def gainXp(self, amount):
        """
        Give experience.
        Caps at the most xp required for a battle
        (Can't level up twice after one battle)
        """
        self.xp = self.xp + amount
        while self.xp >= self.level * 10:
            Op.add(self.name + " leveled up!")
            Op.display()
            self.levelUp()

    def levelUp(self):
        """
        Increases level
        """
        self.xp = 0
        self.level += 1
        self.customizationPoints += 1
        for active in self.actives:
            active.customizationPoints += 1
        for passive in self.passives:
            passive.customizationPoints += 1
        for item in self.equippedItems:
            item.customizationPoints += 1

        self.calcStats()
        self.remHp = self.maxHp
        self.displayData()

    """
    Character management
    """

    def chooseItems(self):
        self.displayItems()

        if len(self.equippedItems) == 0 or choose("Do you wish to change these items?", ("yes", "no")) == "yes":
            for item in self.equippedItems:
                item.unequip()

            items = self.team.get_available_items()

            if len(items) <= 3:
                for item in items:
                    item.equip(self)
                    self.equippedItems.append(item)
            else:
                for item in items:
                    item.displayData()

            items = self.team.get_available_items()
            while (len(self.equippedItems) < 3) and (len(items) is not 0):
                item = choose("Which item do you want to equip?", items)
                item.equip(self)
                self.equippedItems.append(item)
                items = self.team.get_available_items()

            self.displayItems()

    def manage(self):
        options = ["Quit", self]

        if len(self.team.inventory) > 0:
            options.append("Equipped items")

        for item in self.equippedItems:
            item.displayData()
            options.append(item)

        for passive in self.passives:
            passive.displayData()
            options.append(passive)

        for active in self.actives:
            active.displayData()
            options.append(active)

        options.reverse()

        customize = choose("What do you want to customize?", options)
        if customize != "Quit":
            if customize == 'Equipped items':
                self.chooseItems()
            customize.customizeMenu()

class EnemyCharacter(AbstractCharacter):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**dict(kwargs, type="EnemyCharacter"))

    """
    Creates all the default
    enemies in the enemy directory
    """
    @classmethod
    def generateEnemies(cls):
        lightning = EnemyCharacter(
            name="Lightning Entity",
            element="lightning",
            stats={
                "energy" : 10,
                "resistance" : -10
            }
        )
        #lightning.displayData()
        lightning.save()

        rain = EnemyCharacter(
            name="Rain Entity",
            element="rain",
            stats={
                "potency" : 10,
                "control" : -10
            }
        )
        #rain.displayData()
        rain.save()

        hail = EnemyCharacter(
            name="Hail Entity",
            element = "hail",
            stats={
                "resistance" : 10,
                "luck" : -10
            }
        )
        #hail.displayData()
        hail.save()

        wind = EnemyCharacter(
            name="Wind Entity",
            element = "wind",
            stats={
                "luck" : 10,
                "potency" : -10
            }
        )
        #wind.displayData()
        wind.save()

        stone = EnemyCharacter(
            name="Stone Soldier",
            element="stone",
            stats={
                "control":5,
                "resistance":10,
                "luck":-5,
                "energy":-5,
                "potency":-5
            }
        )
        #stone.displayData()
        stone.save()

    """
    saves this enemy to the enemy directory
    """
    def save(self):
        saveSerializable(self, ENEMY_DIR)

    @classmethod
    def loadEnemy(cls, enemyName: str)->"EnemyCharacter":
        return loadSerializable(enemyName, ENEMY_DIR, AbstractCharacter)

    """
    AI stuff
    """
    def bestActive(self):
        best = self.actives[0]
        bestDmg = 0
        Dp.add("----------")
        for active in self.actives:
            if active.canUse():
                dmg = self.team.enemy.active.calcDmgTaken(self, active)
                if dmg > bestDmg:
                    best = active
                    bestDmg = dmg
                Dp.add("Damage with " + active.name + ": " + str(dmg))
        Dp.add("----------")
        Dp.dp()
        return best

    """
    Used to help the AI
    choose what active
    to use
    """
    def whatActive(self):
        if self.team.switched_in:
            sw = 0.75
        else:
            sw = 1.0

        """
        Can you get multiple KOes?
        """
        """
        for active in self.actives:
            if not active.canUse(self) or not type(active) == type(AllAttack("test", 0)):
                continue
            koes = 0
            for member in self.team.enemy.membersRem:
                if member.calcDmgTaken(self, active) * sw >= member.remHp:
                    koes += 1
            if koes >= 2:
                return active
        """
        """
        Can you get a KO?
        """
        canKo = []
        for active in self.actives:
            if active.canUse():
                if self.team.enemy.active.calcDmgTaken(self, active) * sw >= self.team.enemy.active.remHp:
                    canKo.append(active)

        if len(canKo) == 1:
            return canKo[0]
        """
        If you cannot KO...
        """
        return self.bestActive()

    def chooseActive(self):
        self.whatActive().use()
