"""
A Character is an entity within the game who has various stats and attributes.
"""



from battle.events import ActionRegister, UPDATE_EVENT
from maelstrom.dataClasses.customizable import AbstractCustomizable
from maelstrom.dataClasses.stat_classes import Stat
from util.stringUtil import entab, lengthOfLongest
from util.utilities import STATS



class Character(AbstractCustomizable):

    def __init__(self, **kwargs):
        """
        required kwargs:
        - name : str
        - customizationPoints : int (defaults to 0)
        - element : str
        - level : int (defaults to 1)
        - xp : int (defaults to 0)
        - actives : list of AbstractActives. Throws an error if not set
        - passives : list of AbstractPassives. Defaults to empty list
        - equippedItems : list of Items. Defaults to an empty list
        - stats: object{ str : int } (defaults to 0 for each stat in STATS not given in the object)
        """

        super().__init__(**dict(kwargs, type="Character"))
        self.maxHp = 100

        self.element = kwargs["element"]
        self.level = kwargs.get("level", 1)
        self.xp = int(kwargs.get("xp", 0))

        self.actives = []
        self.passives = []
        self.equippedItems = []
        for active in kwargs["actives"]:
            self.actives.append(active)
        for passive in kwargs.get("passives", []):
            self.passives.append
            (passive)
        for item in kwargs.get("equippedItems", []):
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

    def equipItem(self, item: "Item"):
        self.equippedItems.append(item)
        item.setEquipped(True)

    # HP defined here
    def initForBattle(self):
        self.actionRegister.clear()
        self.calcStats()

        # don't need to do anything with actives

        for passive in self.passives:
            passive.registerTo(self)

        for item in self.equippedItems:
            item.registerTo(self)

        self.remHp = self.maxHp
        self.energy = int(self.getStatValue("energy") / 2.0)

    def addActionListener(self, enumType, action):
        self.actionRegister.addActionListener(enumType, action)

    def fireActionListeners(self, enumType, event=None):
        self.actionRegister.fire(enumType, event)

    def getHpPerc(self):
        """
        Returns as a value between 0 and 100
        """
        return int((float(self.remHp) / float(self.maxHp) * 100.0))

    def getDisplayData(self)->str:
        self.calcStats()
        ret = [
            f'{self.name} Lv. {self.level} {self.element}',
            entab(f'{self.xp} / {self.level * 10} XP')
        ]

        ret.append("STATS:")
        width = lengthOfLongest(STATS)
        for stat in STATS:
            ret.append(entab(f'{stat.ljust(width)}: {int(self.getStatValue(stat))}'))

        ret.append("ACTIVES:")
        for active in self.actives:
            ret.append(f'* {active.description}')

        ret.append("PASSIVES:")
        for passive in self.passives:
            ret.append(f'* {passive.description}')

        ret.append("ITEMS:")
        for item in self.equippedItems:
            ret.append(f'* {str(item)}')

        return "\n".join(ret)

    """
    Battle functions:
    Used during battle
    """

    # TODO add ID checking to prevent doubling up
    def boost(self, boost):
        """
        Increase or lower stats in battle. Returns the boost this receives with its
        potency stat factored in
        """
        mult = 1 + self.getStatValue("potency") / 100
        boost = boost.copy()
        boost.amount *= mult
        self.stats[boost.stat_name].boost(boost)
        return boost

    def heal(self, percent):
        """
        Restores HP. Converts an INTEGER to a percentage. Returns the amount of HP
        healed.
        """
        mult = 1 + self.getStatValue("potency") / 100
        healing = self.maxHp * (float(percent) / 100)
        self.remHp = self.remHp + healing * mult

        if self.remHp > self.maxHp:
            self.remHp = self.maxHp

        return int(healing)

    def harm(self, percent):
        """
        returns the actual amount of damage inflicted
        """
        mult = 1 - self.getStatValue("potency") / 100
        harming = self.maxHp * (float(percent) / 100)
        amount = int(harming * mult)
        self.takeDmg(amount)
        return amount

    def takeDmg(self, dmg):
        self.remHp -= dmg
        self.remHp = int(self.remHp)
        return dmg

    def gainEnergy(self, amount):
        """
        Returns the amount of energy gained
        """
        mult = 1 + self.getStatValue("potency") / 100
        amount = int(amount * mult)
        self.energy += amount

        if self.energy > self.getStatValue("energy"):
            self.energy = self.getStatValue("energy")

        return amount

    def loseEnergy(self, amount):
        self.energy -= amount
        if self.energy < 0:
            self.energy = 0

    def update(self):
        self.fireActionListeners(UPDATE_EVENT, self)
        self.gainEnergy(self.getStatValue("energy") * 0.15)
        for stat in self.stats.values():
            stat.update()

    def isKoed(self):
        return self.remHp <= 0

    """
    Post-battle actions:
    Occur after battle
    """

    def gainXp(self, amount)->"List<str>":
        """
        Give experience, possibly leveling up this character.

        Returns a list of messages to display, if any.
        """
        msgs = []
        self.xp += amount
        while self.xp >= self.level * 10:
            msgs.append(f'{self.name} leveled up!')
            self.xp -= self.level * 10
            self.levelUp()
            msgs.append(self.getDisplayData())
        self.xp = int(self.xp)
        return msgs

    def levelUp(self):
        self.level += 1
        self.customizationPoints += 1

        self.calcStats()
        self.remHp = self.maxHp
