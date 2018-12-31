from stat_classes import Stat
#from characters import AbstractCharacter
"""
An AbstractUpgradable is anything that the player can change as their characters level up.

TODO: make player characters, attacks, passives, and items extend this
"""

class AbstractUpgradable(object):
    """
    The abstract base class for anything that the player can customize as they level up
    """
    next_id = 0
    def __init__(self, name: str):
        self.name = name
        self.id = AbstractUpgradable.next_id
        AbstractUpgradable.next_id += 1

        self.attributes = {} #what can be customized
        self.level = 0
        self.customization_points = 0

        self.user = None

    def set_user(self, user):#: AbstractCharacter):
        """
        Sets this' user
        """
        self.user = user

    def calc_all(self):
        """
        Calculates all this' stats
        """
        for stat in self.attributes.values():
            stat.calc()

    def add_attr(self, attr_id: str, value: Stat):
        """
        Sets an attribute for this upgradable.
        """
        self.attributes[attr_id] = value

    def get_stat(self, attr_id: str) -> float:
        """
        Gets the value of a given stat (attribute).
        If the attribute does not exist, returns 0
        """
        ret = 0.0
        if attr_id in self.attributes:
            ret = self.attributes[attr_id].get()

        return ret

    def set_base(self, stat_name: str, base: int):
        """
        Re-sets a stat's base calculation value
        """
        self.attributes[stat_name].set_base(base)

    def __str__(self) -> str:
        return self.name

    def get_save_code(self) -> str:
        """
        returns a save code,
        which can be used to reconstuct this object
        """
        ret = self.name + "{"
        for k, v in self.attributes.items():
            ret += '\t\"' + k + '\" : \"' + str(v.get_base()) + '\"\n'
        ret += "}"

        return ret
