from utilities import contains, ignore_text, choose, ELEMENTS, STATS, Dp
from stat_classes import Stat
from attacks import AbstractActive
from passives import AbstractPassive
from item import Item, ItemSet
from events import *
from customizable import AbstractCustomizable
from output import Op
import json

from pathlib import Path
import os


from file import writeCsvFile

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
    - customPoints : int
    - element : str
    - level : int
    - XP : int
    - attacks : list
    - passives : list
    - equipped_items : list
    - stats: object
    """
    def __init__(self, **kwargs):
        super(AbstractCharacter, self).__init__(**kwargs)
        self.max_hp = 100

        self.element = kwargs["element"]
        self.level = kwargs["level"]
        self.XP = kwargs["XP"]

        self.attacks = kwargs["attacks"]
        self.passives = kwargs["passives"]
        self.equipped_items = kwargs["equipped_items"]
        for stat in STATS:
            self.addStat(Stat(stat, lambda base: 20.0 + float(base), kwargs["stats"][stat]))
        self.addSerializedAttributes(
            "element",
            "XP",
            "level",
            "attacks",
            "passives",
            "equipped_items"
        )

    """
    Returns a deep copy of this character
    """
    def copy(self)->'AbstractCharacter':
        return AbstractCharacter.read_json(self.toJsonDict())

    """
    Reads a JSON object as a dictionary, then converts it to an AbstractCharacter
    """
    @staticmethod
    def loadJson(jdict) -> 'AbstractCharacter':
        ctype = jdict["type"]

        #name = jdict["name"]
        #element = jdict["element"]
        #level = int(jdict["level"])
        #xp = int(jdict["XP"])
        #actives = jdict["attacks"]
        #passives = jdict["passives"]
        #items = jdict["equipped_items"]
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
        #ret.set_element(element)
        #ret.level = level
        #ret.XP = xp
        """
        for k, v in jdict.items():
            if type(v) == type({}) and v.get('type', 'NO TYPE') == 'Stat':
                ret.set_base(k, int(v.get('base', 0)))

        for active in jdict.get('attacks', []):
            #for some reason, I have to reconver to a dictionary,
            #because active is a string
            ret.add_active(AbstractActive.read_json(active))
        for passive in jdict.get('passives', []):
            ret.add_passive(AbstractPassive.read_json(passive))
        for item in jdict.get('equipped_items', []):
            ret.equip_item(Item.read_json(item))
        """
        return ret


    @staticmethod
    def read_default_player() -> 'AbstractCharacter':
        """
        reads the data from files/base_character, then converts it to a character
        """
        ret = AbstractCharacter.create_default_player()
        with open('files/base_character.json') as file:
            ret = AbstractCharacter.read_json(json.loads(file.read()))

        return ret

    """
    The new default method.
    """
    @staticmethod
    def createDefaultPlayer()->"PlayerCharacter":
        attacks = AbstractActive.get_defaults()
        attacks.append(AbstractActive.get_default_bolt("lightning"))
        dict = {
            "name" : "Default Player Character",
            "customPoints" : 0,
            "element" : "lightning",
            "level" : 1,
            "XP" : 0,
            "attacks" : attacks,
            "passives" : AbstractPassive.get_defaults(),
            "equipped_items" : [],
            "stats" : {stat: 0 for stat in STATS}
        }

        player = PlayerCharacter(**dict)
        return player

    # old method
    @staticmethod
    def create_default_player() -> 'PlayerCharacter':
        """
        Used to create a default character to use as a base for all other characters
        """
        ret = PlayerCharacter('NO NAME')
        ret.add_default_actives()
        ret.add_default_passives()
        ret.equip_default_items()
        return ret

    def set_element(self, element: str):
        """
        Shortens the process of setting
        a character's element, so I don't
        have to manually edit each active
        """
        for active in self.attacks:
            print(active.name)
            print(element)
            print(self.element)
            if self.element.lower() in active.name.lower():
                active.name = active.name.lower()
                print(active.name)
                active.name = active.name.replace(self.element.lower(), element.lower())
        self.element = element

    def add_active(self, active: 'AbstractActive'):
        """

        """
        self.attacks.append(active)
        active.set_user(self)
        active.calc_all()

    def add_default_actives(self):
        self.add_active(AbstractActive.get_default_bolt(self.element))
        for active in AbstractActive.get_defaults():
            self.add_active(active)

    def add_passive(self, passive: 'AbstractPassive'):
        """
        """
        self.passives.append(passive)
        passive.set_user(self)
        passive.calc_all()

    def add_default_passives(self):
        for passive in AbstractPassive.get_defaults():
            self.add_passive(passive)

    def equip_item(self, item: 'Item'):
        """
        """
        self.equipped_items.append(item)
        item.set_user(self)
        item.equip(self)
        item.calc_all()

    def equip_default_items(self):
        for item in Item.get_defaults():
            self.equip_item(item)

    # HP defined here
    def init_for_battle(self):
        """
        Prepare for battle!
        """
        self.reset_action_registers()

        self.calc_all()

        for attack in self.attacks:
            attack.set_user(self)
            attack.init_for_battle()

        for passive in self.passives:
            passive.set_user(self)
            passive.init_for_battle()

        for item in self.equipped_items:
            item.set_user(self)
            item.apply_boosts()

        # this part down here checks if we should get the 3-piece set bonus from our items
        check_set = None
        set_total = 0
        for item in self.equipped_items:
            if item.set_name != None:
                if check_set == None:
                    check_set = item.set_name
                if item.set_name == check_set:
                    set_total += 1
            if set_total == 3:
                ItemSet.get_set_bonus(check_set).f(self)

        self.HP_rem = self.max_hp
        self.energy = int(self.getStatValue("energy") / 2.0)

    # action register class?
    def reset_action_registers(self):
        """
        Action registers are used to
        hold functions which should be
        invoked whenever a specific
        condition is met, such as being
        hit. They should each take an
        extendtion of AbstractEvent as
        a paramter
        """
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
    Data obtaining functions:
    Used to get data about a character
    """
    def hp_perc(self):
        """
        Returns as a value between 0 and 100
        """
        return int((float(self.HP_rem) / float(self.max_hp) * 100.0))

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
        for attack in self.attacks:
            Op.add("-" + attack.name)

        Op.add("PASSIVES:")
        for passive in self.passives:
            Op.add("-" + passive.name)

        Op.add("ITEMS:")
        for item in self.equipped_items:
            Op.add("-" + item.name)

        Op.add(str(self.XP) + "/" + str(self.level * 10))
        Op.display()

    def get_short_desc(self):
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
        self.attributes[boost.stat_name].boost(boost)

    def heal(self, percent):
        """
        Restores HP.
        Converts an INTEGER
        to a percentage.
        """
        mult = 1 + self.getStatValue("potency") / 100
        healing = self.max_hp * (float(percent) / 100)
        self.HP_rem = self.HP_rem + healing * mult

        Op.add(self.name + " healed " + str(int(healing)) + " HP!")
        Op.display()

        if self.HP_rem > self.max_hp:
            self.HP_rem = self.max_hp

    def harm(self, percent):
        mult = 1 - self.getStatValue("potency") / 100
        harming = self.max_hp * (float(percent) / 100)
        self.direct_dmg(harming * mult)
        Op.add(self.name + " took " + str(int(harming * mult)) + " damage!")
        Op.display()

    def direct_dmg(self, dmg):
        self.HP_rem -= dmg
        self.HP_rem = int(self.HP_rem)
        self.team.updateMembersRem()

    def gain_energy(self, amount):
        """
        Increase your energy.
        """
        self.energy = self.energy + amount

        if self.energy > self.getStatValue("energy"):
            self.energy = self.getStatValue("energy")

        self.energy = int(self.energy)

    def lose_energy(self, amount):
        """
        Decrease your energy
        """
        self.energy = self.energy - amount
        if self.energy < 0:
            self.energy = 0

    # stat.displayData in here
    def update(self):
        self.update_action_registers()
        for action in self.on_update_actions:
            action["function"]()

        self.gain_energy(self.getStatValue("energy") * 0.15)
        for stat in self.attributes.values():
            stat.update()
            #stat.displayData();

    """
    Damage calculation
    """
    def calc_DMG(self, attacker, attack_used):
        """
        MHC is not checked here so that it doesn't
        mess with AI
        """
        damage = 0
        for damage_type, value in attack_used.damages.items():
            damage += value
        damage *= attacker.getStatValue("control") / self.getStatValue("resistance")

        if attacker.team.switched_in:
            damage = damage * 0.75

        return damage

    def take_DMG(self, attacker, attack_used):
        dmg = self.calc_DMG(attacker, attack_used)
        dmg = dmg * attack_used.calc_MHC()
        Op.add(attacker.name + " struck " + self.name)
        Op.add("for " + str(int(dmg)) + " damage")
        Op.add("using " + attack_used.name + "!")
        Op.display()

        event = OnHitEvent("Attack", attacker, self, attack_used, dmg)
        event.displayData()

        for passive in self.on_hit_taken_actions:
            passive["function"](event)

        for passive in attacker.on_hit_given_actions:
            passive["function"](event)

        self.direct_dmg(dmg)

    def check_if_KOed(self):
        """
        Am I dead yet?
        """
        return self.HP_rem <= 0

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

    def choose_attack(self):
        attack_options = []
        for attack in self.attacks:
            if attack.can_use():
                attack_options.append(attack)

        choose("What attack do you wish to use?", attack_options).use()

    """
    Post-battle actions:
    Occur after battle
    """
    def gain_XP(self, amount):
        """
        Give experience.
        Caps at the most XP required for a battle
        (Can't level up twice after one battle)
        """
        self.XP = self.XP + amount
        while self.XP >= self.level * 10:
            Op.add(self.name + " leveled up!")
            Op.display()
            self.level_up()

    def level_up(self):
        """
        Increases level
        """
        self.XP = 0
        self.level += 1
        self.customPoints += 1
        for active in self.attacks:
            active.customPoints += 1
        for passive in self.passives:
            passive.customPoints += 1
        for item in self.equipped_items:
            item.customPoints += 1

        self.calc_all()
        self.HP_rem = self.max_hp
        self.displayData()

    """
    Character management
    """

    def choose_items(self):
        self.display_items()

        if len(self.equipped_items) == 0 or choose("Do you wish to change these items?", ("yes", "no")) == "yes":
            for item in self.equipped_items:
                item.unequip()

            items = self.team.get_available_items()

            if len(items) <= 3:
                for item in items:
                    item.equip(self)
                    self.equipped_items.append(item)
            else:
                for item in items:
                    item.displayData()

            items = self.team.get_available_items()
            while (len(self.equipped_items) < 3) and (len(items) is not 0):
                item = choose("Which item do you want to equip?", items)
                item.equip(self)
                self.equipped_items.append(item)
                items = self.team.get_available_items()

            self.display_items()

    def manage(self):
        """
        This will replace customize
        """
        options = ["Quit"]

        if len(self.team.inventory) > 0:
            options.append("Equipped items")

        for item in self.equipped_items:
            item.displayData()
            options.append(item)

        for passive in self.passives:
            passive.displayData()
            options.append(passive)

        for attack in self.attacks:
            attack.displayData()
            options.append(attack)

        options.reverse()

        customize = choose("What do you want to customize?", options)
        if customize != "Quit":
            if customize == 'Equipped items':
                self.choose_items()
            customize.customize()



class EnemyCharacter(AbstractCharacter):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__("EnemyCharacter", kwargs)

    """
    AI stuff
    """
    def best_attack(self):
        best = self.attacks[0]
        highest_dmg = 0
        Dp.add("----------")
        for attack in self.attacks:
            if attack.can_use():
                dmg = self.team.enemy.active.calc_DMG(self, attack)
                if dmg > highest_dmg:
                    best = attack
                    highest_dmg = dmg
                Dp.add("Damge with " + attack.name + ": " + str(dmg))
        Dp.add("----------")
        Dp.dp()
        return best

    def what_attack(self):
        """
        Used to help the AI
        choose what attack
        to use
        """
        if self.team.switched_in:
            sw = 0.75
        else:
            sw = 1.0

        """
        Can you get multiple KOes?
        """
        """
        for attack in self.attacks:
            if not attack.can_use(self) or not type(attack) == type(AllAttack("test", 0)):
                continue
            koes = 0
            for member in self.team.enemy.members_rem:
                if member.calc_DMG(self, attack) * sw >= member.HP_rem:
                    koes += 1
            if koes >= 2:
                return attack
        """
        """
        Can you get a KO?
        """
        can_ko = []
        for attack in self.attacks:
            if attack.can_use():
                if self.team.enemy.active.calc_DMG(self, attack) * sw >= self.team.enemy.active.HP_rem:
                    can_ko.append(attack)

        if len(can_ko) == 1:
            return can_ko[0]
        """
        If you cannot KO...
        """
        return self.best_attack()

    def choose_attack(self):
        self.what_attack().use()

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

if __name__ == "__main__":
    pass
