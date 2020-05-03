from utilities import choose, ELEMENTS, STATS, Dp
from stat_classes import Stat
from actives import AbstractActive
from passives import AbstractPassive
from item import Item, ItemSet
from events import *
from customizable import AbstractCustomizable
from output import Op
import json

# these two used for enemy cache
from pathlib import Path
import os

"""
Characters
"""
ENEMY_DIRECTORY = 'files/enemy_characters'
ENEMY_CACHE = {} #cached results of loading enemy files

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
    - equippedItems : list (defaults to [])
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
        for item in kwargs.get("equippedItems", []):
            self.equipItem(item)

        for stat in STATS:
            self.addStat(Stat(stat, lambda base: 20.0 + float(base), kwargs.get("stats", {}).get(stat, 0)))
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
    def copy(self)->'AbstractCharacter':
        return AbstractCharacter.loadJson(self.toJsonDict())

    """
    Reads a JSON object as a dictionary, then converts it to an AbstractCharacter
    """
    @staticmethod
    def loadJson(jdict) -> 'AbstractCharacter':
        ctype = jdict["type"]
        jdict["actives"] = [AbstractActive.read_json(data) for data in jdict["actives"]]
        #name = jdict["name"]
        #element = jdict["element"]
        #level = int(jdict["level"])
        #xp = int(jdict["xp"])
        #actives = jdict["actives"]
        #passives = jdict["passives"]
        #items = jdict["equippedItems"]
        #custom_points = int(jdict["customPoints"])

        ret = None

        if ctype == 'PlayerCharacter':
            ret = PlayerCharacter(**jdict)
        elif ctype == 'EnemyCharacter':
            ret = EnemyCharacter(**jdict)
        else:
            raise Exception('Type not found! ' + ctype)

        # oh, this is so horrible!!!
        #ret.customPoints = custom_points
        #ret.level = level
        #ret.xp = xp
        """
        for k, v in jdict.items():
            if type(v) == type({}) and v.get('type', 'NO TYPE') == 'Stat':
                ret.set_base(k, int(v.get('base', 0)))

        for active in jdict.get('actives', []):
            #for some reason, I have to reconver to a dictionary,
            #because active is a string
            ret.addActive(AbstractActive.read_json(active))
        for passive in jdict.get('passives', []):
            ret.add_passive(AbstractPassive.read_json(passive))
        for item in jdict.get('equippedItems', []):
            ret.equipItem(Item.read_json(item))
        """
        return ret

    def addActive(self, active: 'AbstractActive'):
        self.actives.append(active)
        active.set_user(self)
        active.calc_all()

    def addPassive(self, passive: 'AbstractPassive'):
        """
        """
        self.passives.append(passive)
        passive.set_user(self)
        passive.calc_all()

    def equipItem(self, item: 'Item'):
        self.equippedItems.append(item)
        item.set_user(self)
        item.equip(self)
        item.calc_all()

    # HP defined here
    def initForBattle(self):
        self.resetActionRegisters()
        self.calcStats()

        for active in self.actives:
            active.set_user(self)
            active.initForBattle()

        for passive in self.passives:
            passive.set_user(self)
            passive.initForBattle()

        for item in self.equippedItems:
            item.set_user(self)
            item.apply_boosts()

        # this part down here checks if we should get the 3-piece set bonus from our items
        checkSet = None
        setTotal = 0
        for item in self.equippedItems:
            if item.set_name != None:
                if checkSet == None:
                    checkSet = item.set_name
                if item.set_name == checkSet:
                    setTotal += 1
            if setTotal == 3:
                ItemSet.get_set_bonus(checkSet).f(self)

        self.remHp = self.maxHp
        self.energy = int(self.getStatValue("energy") / 2.0)

    # Redo all of this sometime
    """
    Action registers are used to
    hold functions which should be
    invoked whenever a specific
    condition is met, such as being
    hit. They should each take an
    extendtion of AbstractEvent as
    a paramter
    """
    def resetActionRegisters(self):
        self.on_hit_given_actions = []
        self.on_hit_taken_actions = []
        self.on_update_actions = []
    def add_on_hit_given_action(self, action, duration = -1):
        """
        duration is how long to check for the condition
        """
        self.on_hit_given_actions.append({"function":action, "duration":duration})
    def add_on_hit_taken_action(self, action, duration = -1):
        """
        duration of -1 means it lasts forever in battle
        """
        self.on_hit_taken_actions.append({"function":action, "duration":duration})
    def add_on_update_action(self, action, duration = -1):
        """
        """
        self.on_update_actions.append({"function":action, "duration":duration})
    def update_action_registers(self):
        """
        Standard decrement, check, reasign
        pattern I use all the time
        """
        def update(register):
            new = []
            for action in register:
                action["duration"] -= 1
                # don't check if negative,
                # that way I can make stuff last forever
                if action["duration"] != 0:
                    new.append(action)
        update(self.on_hit_given_actions)
        update(self.on_hit_taken_actions)
        update(self.on_update_actions)


    """
    Returns as a value between 0 and 100
    """
    def getHpPerc(self):
        return int((float(self.remHp) / float(self.maxHp) * 100.0))

    def displayData(self):
        """
        Print info on a character
        """
        self.calcStats()
        Op.add("Lv. " + str(self.level) + " " + self.name)
        Op.add(self.element)

        Op.add("STATS:")
        for stat in STATS:
            Op.add(stat + ": " + str(int(self.getStatValue(stat))))

        Op.add("ACTIVES:")
        for active in self.actives:
            Op.add("-" + active.name)

        Op.add("PASSIVES:")
        for passive in self.passives:
            Op.add("-" + passive.name)

        Op.add("ITEMS:")
        for item in self.equippedItems:
            Op.add("-" + item.name)

        Op.add(str(self.xp) + "/" + str(self.level * 10))
        Op.display()

    def getShortDesc(self):
        """
        returns a short description of the character
        """
        return self.name + " Lv " + str(self.level) + " " + self.element

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

    # stat.displayData in here
    def update(self):
        self.update_action_registers()
        for action in self.on_update_actions:
            action["function"]()

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
        damage = 0
        for damage_type, value in activeUsed.damages.items():
            damage += value
        damage *= attacker.getStatValue("control") / self.getStatValue("resistance")

        if attacker.team.switched_in:
            damage = damage * 0.75

        return damage

    def struckBy(self, attacker, activeUsed):
        dmg = self.calcDmgTaken(attacker, activeUsed)
        dmg = dmg * activeUsed.calc_MHC()
        Op.add(attacker.name + " struck " + self.name)
        Op.add("for " + str(int(dmg)) + " damage")
        Op.add("using " + activeUsed.name + "!")
        Op.display()

        event = OnHitEvent("Attack", attacker, self, activeUsed, dmg)
        event.displayData()

        for passive in self.on_hit_taken_actions:
            passive["function"](event)

        for passive in attacker.on_hit_given_actions:
            passive["function"](event)

        self.takeDmg(dmg)

    def isKoed(self):
        return self.remHp <= 0

    @staticmethod
    def load_from_file(file_path: str) -> 'AbstractCharacter':
        """
        Reads a json file, then returns the character contained in that file
        """
        ret = None

        try:
            with open(file_path, 'rt') as file:
                ret = AbstractCharacter.read_json(json.loads(file.read()))
        except FileNotFoundError as ex:
            Op.add('Could not find file ' + file_path)
            Op.add(str(ex))
            Op.display()

        return ret


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
            if active.can_use():
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
        self.customPoints += 1
        for active in self.actives:
            active.customPoints += 1
        for passive in self.passives:
            passive.customPoints += 1
        for item in self.equippedItems:
            item.customPoints += 1

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
        options = ["Quit"]

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
            customize.customize()



class EnemyCharacter(AbstractCharacter):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**dict(kwargs, type="EnemyCharacter"))

    """
    AI stuff
    """
    def bestActive(self):
        best = self.actives[0]
        bestDmg = 0
        Dp.add("----------")
        for active in self.actives:
            if active.can_use():
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
            if not active.can_use(self) or not type(active) == type(AllAttack("test", 0)):
                continue
            koes = 0
            for member in self.team.enemy.members_rem:
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
            if active.can_use():
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

    """
    Reads an enemy file, if it exists.
    If force is True, searches through the enemy directory for
    that enemy's save file, then loads that enemy, caching it in the
    enemy cache.

    If force is False, will first check if the enemy has already been
    cached.
    """
    @staticmethod
    def load_enemy(name=' ', force=False, all=False) -> 'EnemyCharacter':
        ret = None

        if not force and name.title in ENEMY_CACHE:
            ret = ENEMY_CACHE[name.title]
        else:
            for path in Path(ENEMY_DIRECTORY).iterdir():
                print(str(path))
                file_name = str(path).split(os.sep)[-1]
                print(file_name)
                char_name = file_name.split('.')[0].replace('_', ' ').title() # get rid of file extention
                print(char_name)
                if all or name.title().replace('_', ' ') == char_name:
                    ret = AbstractCharacter.load_from_file(str(path))
                    ENEMY_CACHE[char_name] = ret

        if ret is None:
            raise FileNotFoundError('Enemy not found in ' + ENEMY_DIRECTORY + ': ' + name + ' Did you forget to call .save() on that enemy?')

        return ret.copy()
