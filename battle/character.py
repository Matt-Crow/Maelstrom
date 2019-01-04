from utilities import contains, ignore_text, choose, ELEMENTS, STATS, Dp
from stat_classes import Stat
from attacks import AbstractActive
from passives import AbstractPassive
from item import Item, ItemSet
from events import *
from upgradable import AbstractUpgradable
from output import Op
from enemies import enemies


"""
Characters.

Have to keep all 3 classes in one file because of circular depenancy

CLEAN UP THIS MESS
"""
class AbstractCharacter(AbstractUpgradable):
    """
    A Class containing all the info for a character
    """


    """
    Initializers:
    Used to 'build' the characters
    """
    def __init__(self, name):
        """
        """
        super(AbstractCharacter, self).__init__(name)
        self.set_type('AbstractCharacter')
        self.max_hp = 100

        for stat in STATS:
            self.add_attr(stat, Stat(stat, battle_stat, 10))

        for element in ELEMENTS:
            self.add_attr(element + " damage multiplier", Stat(element + " damage multiplier", mult_red_stat, 10))
            self.add_attr(element + " damage reduction", Stat(element + " damage reduction", mult_red_stat, 10))

        self.element = 'NO ELEMENT'
        self.level = 1
        self.XP = 0

        self.attacks = [AbstractActive.get_default_bolt(self.element)]
        self.passives = []

        #self.add_default_actives()
        self.set_passives_to_defaults()
        for attack in self.attacks:
            attack.set_user(self)
        self.equipped_items = []

        self.equip_default_items()

        self.track_attr('element')
        self.track_attr('XP')
        self.track_attr('level')
        self.track_attr('attacks')
        self.track_attr('passives')
        self.track_attr('equipped_items')


    @staticmethod
    def read_json(json: dict) -> 'AbstractCharacter':
        """
        Reads a JSON object as a dictionary, then converts it to an AbstractCharacter
        """
        name = json.get('name', 'NAME NOT FOUND')
        custom_points = int(json.get('customization_points', 0))
        rtype = json.get('type', 'TYPE NOT FOUND')
        element = json.get('element', 'ELEMENT NOT FOUND')
        level = int(json.get('level', 1))
        xp = int(json.get('XP', 0))

        ret = None

        if rtype == 'PlayerCharacter':
            ret = PlayerCharacter(name)
        elif rtype == 'EnemyCharacter':
            ret = EnemyCharacter(name)
        else:
            raise Exception('Type not found! ' + rtype)

        ret.customization_points = custom_points
        ret.element = element
        ret.level = level
        ret.XP = xp

        for k, v in json.items():
            if k not in ret.track and type(v) not in (type([]), type({})):
                ret.set_base(k, int(v))

        for active in json.get('attacks', []):
            print(active)
            ret.add_active(AbstractActive.read_json(active))

        return ret


    def add_active(self, active: 'AbstractActive'):
        """

        """
        self.attacks.append(active)
        active.set_user(self)
        active.calc_all()


    #temporary
    def add_default_actives(self):
        for active in AbstractActive.get_defaults():
            self.attacks.append(active)
            active.set_user(self)
            active.calc_all()

    #temporary
    def set_passives_to_defaults(self):
        for passive in AbstractPassive.get_defaults():
            self.passives.append(passive)
            passive.set_user(self)
            passive.calc_all()

    def equip_default_items(self):
        for item in Item.get_defaults():
            self.equipped_items.append(item)
            item.set_user(self)
            item.equip(self)
            item.calc_all()


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
        self.energy = int(self.get_stat("energy") / 2.0)

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


    def display_data(self):
        """
        Print info on a character
        """
        self.calc_all()
        Op.add("Lv. " + str(self.level) + " " + self.name)
        Op.add(self.element)

        Op.add("STATS:")
        for stat in STATS:
            Op.add(stat + ": " + str(int(self.get_stat(stat))))

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
        mult = 1 + self.get_stat("potency") / 100
        self.attributes[boost.stat_name].boost(boost)


    def heal(self, percent):
        """
        Restores HP.
        Converts an INTEGER
        to a percentage.
        """
        mult = 1 + self.get_stat("potency") / 100
        healing = self.max_hp * (float(percent) / 100)
        self.HP_rem = self.HP_rem + healing * mult

        Op.add(self.name + " healed " + str(int(healing)) + " HP!")
        Op.display()

        if self.HP_rem > self.max_hp:
            self.HP_rem = self.max_hp

    def harm(self, percent):
        mult = 1 - self.get_stat("potency") / 100
        harming = self.max_hp * (float(percent) / 100)
        self.direct_dmg(harming * mult)
        Op.add(self.name + " took " + str(int(harming * mult)) + " damage!")
        Op.display()

    def direct_dmg(self, dmg):
        self.HP_rem -= dmg
        self.HP_rem = int(self.HP_rem)
        self.team.update_members_rem()

    def gain_energy(self, amount):
        """
        Increase your energy.
        """
        self.energy = self.energy + amount

        if self.energy > self.get_stat("energy"):
            self.energy = self.get_stat("energy")

        self.energy = int(self.energy)

    def lose_energy(self, amount):
        """
        Decrease your energy
        """
        self.energy = self.energy - amount
        if self.energy < 0:
            self.energy = 0

    # stat.display_data in here
    def update(self):
        self.update_action_registers()
        for action in self.on_update_actions:
            action["function"]()

        self.gain_energy(self.get_stat("energy") * 0.15)
        for stat in self.stats:
            stat.update()
            #stat.display_data();

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
            damage += value * (attacker.get_stat(damage_type + " damage multiplier") / self.get_stat(damage_type + " damage reduction"))
        damage *= attacker.get_stat("control") / self.get_stat("resistance")

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
        event.display_data()

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











class PlayerCharacter(AbstractCharacter):
    """
    A PlayerCharacter is a Character controlled by a player.
    Currently, each player has only one character, but I will
    leave that open to adjustment
    """
    def __init__(self, name):
        """
        name is the name of the Player character.
        """
        super(self.__class__, self).__init__(name)
        self.set_type('PlayerCharacter')


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
        self.customization_points += 1
        for active in self.attacks:
            active.customization_points += 1
        for passive in self.passives:
            passive.customization_points += 1
        for item in self.equipped_items:
            item.customization_points += 1

        self.calc_all()
        self.HP_rem = self.max_hp
        self.display_data()

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
                    item.display_data()

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

        for item in self.equipped_items:
            item.display_data()
            options.append(item)

        for passive in self.passives:
            passive.display_data()
            options.append(passive)

        for attack in self.attacks:
            attack.display_data()
            options.append(attack)

        options.reverse()

        customize = choose("What do you want to customize?", options)
        if customize != "Quit":
            customize.customize()


    def customize(self):
        options = ["Quit"]

        if len(self.team.inventory) > 0:
            options.append("Equipped items")

        options.reverse()

        choice = choose("What do you want to modify?", options)

        if choice == "Equipped items":
            self.choose_items()


    def generate_stat_code(self):
        """
        Generates a sequence used
        during file reading in order
        to copy stats from one play
        session to the next
        """
        ret = "<STATS>: "
        for stat in STATS:
            ret += "/" + str(self.get_stat_data(stat).base_value - 20)

        return ret

    def read_stat_code(self, code):
        """
        Used to load a stat spread
        via a string
        """
        new_stat_bases = []
        broken_down_code = code.split('/')
        use = list()
        for line in broken_down_code:
            if not line.isspace():
                use.append(line)

        ind = 0
        while ind < 5:
            new_stat_bases.append(int(float(use[ind])))
            ind += 1

        self.set_stat_bases(new_stat_bases)

    def generate_save_code(self):
        """
        Used to get all data on this
        character
        """
        ret = ["<NAME>: " + self.name]
        ret.append("<LEVEL>: " + str(self.level))
        ret.append("<XP>: " + str(self.XP))
        ret.append(self.generate_stat_code())

        for type, amount in self.custom_points.items():
            ret.append("<CP> " + type + " customization points: " + str(amount))

        for passive in self.passives:
            for line in passive.generate_save_code():
                ret.append(line)
        for active in self.attacks:
            for line in active.generate_save_code():
                ret.append(line)
        for item in self.team.inventory:
            for line in item.generate_save_code():
                ret.append(line)
        return ret

    def read_save_code(self, code):
        passive_codes = []
        active_codes = []
        item_codes = []

        mode = None
        for line in code:

            line = line.strip()
            if contains(line, "<NAME>:"):
                self.name = ignore_text(line, "<NAME>:").strip()
                mode = None
            elif contains(line, "<LEVEL>:"):
                self.level = int(float(ignore_text(line, "<LEVEL>:")))
                mode = None
            elif contains(line, "<XP>:"):
                self.XP = int(float(ignore_text(line, "<XP>:")))
                mode = None
            elif contains(line, "<STATS>:"):
                self.read_stat_code(ignore_text(line, "<STATS>:"))
                mode = None
            elif contains(line, "<CP>"):
                n = ignore_text(ignore_text(line, "<CP>"), " customization points:")
                n = n.split()
                self.custom_points[n[0]] = int(float(n[1]))
                mode = None
            elif contains(line, "<PASSIVE>:"):
                passive_codes.append(list())
                mode = "PASSIVE"
            elif contains(line, "<ACTIVE>:"):
                active_codes.append(list())
                mode = "ACTIVE"

            elif contains(line, "<ITEM>:"):
                item_codes.append(list())
                mode = "ITEM"

            elif line.isspace():
                mode = "DONE"

            if mode == "PASSIVE":
                passive_codes[-1].append(ignore_text(line, "<PASSIVE>:"))

            if mode == "ACTIVE":
                active_codes[-1].append(ignore_text(line, "<ACTIVE>:"))

            if mode == "ITEM":
                item_codes[-1].append(ignore_text(line, "<ITEM>:"))


        new_passives = []
        for code in passive_codes:
            new_passives.append(AbstractPassive.read_save_code(code))

        for passive in new_passives:
            passive.set_user(self)
        self.passives = new_passives


        new_actives = []
        for code in active_codes:
            new_actives.append(AbstractActive.read_save_code(code))

        for active in new_actives:
            active.set_user(self)
        self.attacks = new_actives


        new_items = []
        for code in item_codes:
            new_items.append(Item.read_save_code(code))
        self.team.inventory = new_items








class EnemyCharacter(AbstractCharacter):
    def __init__(self, name):
        super(self.__class__, self).__init__(name)
        self.set_type('EnemyCharacter')

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
Stat formulae,
used to calculate stat values
"""


def mult_red_stat(base: int) -> float:
    """
    passed in as the formula for multiplication and reduction stats
    """
    return (0.5 + 0.05 * base)


def battle_stat(base: int) -> float:
    """
    passed in as the formula for battle stats
    (damage reduction, multiplication, etc)
    """
    return 10.0 + float(base)
