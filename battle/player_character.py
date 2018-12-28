from characters import AbstractCharacter
from utilities import contains, ignore_text
from passives import AbstractPassive
from attacks import AbstractActive
from item import Item

class PlayerCharacter(AbstractCharacter):
    """
    A PlayerCharacter is a Character controlled by a player.
    Currently, each player has only one character, but I will
    leave that open to adjustment
    """
    def __init__(self, name, data, level):
        """
        name is the name of the Player character.
        data is a Tuple of 5 integers, ranging from -5 to 5
        """
        super(self.__class__, self).__init__(name, data, level)
        self.custom_points = {
            "attack": 0,
            "passive": 0,
            "stat": 0,
            "item": 0
        }

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
            Op.dp()
            self.level_up()

    def level_up(self):
        """
        Increases level
        """
        self.XP = 0
        self.level += 1
        for type in self.custom_points.keys():
            self.custom_points[type] += 1
        self.calc_stats()
        self.HP_rem = self.get_stat("HP")
        self.display_data()

    """
    Character management
    """

    def modify_stats(self):
        for stat in self.stats:
            stat.reset_boosts()
        self.calc_stats()
        self.display_mutable_stats()

        self.get_stat_data(choose("Which stat do you want to increase by 5%?", STATS)).base_value += 1
        self.get_stat_data(choose("Which stat do you want to decrease by 5%?", STATS)).base_value -= 1

        self.calc_stats()
        self.display_mutable_stats()
        self.custom_points["stat"] -= 1

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

    def choose_passive_to_customize(self):
        for passive in self.passives:
            passive.display_data()
        choose("Which passive do you want to modify?", self.passives).customize()
        self.custom_points["passive"] -= 1

    def choose_attack_to_customize(self):
        for attack in self.attacks:
            attack.display_data()
        choose("Which attack do you want to modify?", self.attacks).customize()
        self.custom_points["attack"] -= 1

    def choose_item_to_customize(self):
        for item in self.team.inventory:
            item.display_data()
        choose("Which item do you want to modify?", self.team.inventory).generate_random_enh()
        self.custom_points["item"] -= 1

    def customize(self):
        options = ["Quit"]

        if len(self.team.inventory) > 0:
            options.append("Equipped items")

        for type, points in self.custom_points.items():
            if points > 0:
                options.append(type)

        options.reverse()

        choice = choose("What do you want to modify?", options)

        if choice == "Equipped items":
            self.choose_items()

        elif choice == "passive":
            self.choose_passive_to_customize()

        elif choice == "attack":
            self.choose_attack_to_customize()

        elif choice == "stat":
            self.modify_stats()

        elif choice == "item":
            self.choose_item_to_customize()

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