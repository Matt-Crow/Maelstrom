from stat_classes import Stat
from utilities import choose
import json
from output import Op
"""
An AbstractUpgradable is anything that the player can change as their characters level up.

TODO: make player characters, passives, and items extend this
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
        # str : Stat
        self.customization_points = 5 #need to save to JSON. Currently is test value

        self.user = None
        self.type = "AbstractUpgradable" # used when decoding JSON

        self.track = [
            'name',
            'type',
            'customization_points'
        ] #extra properties that need to be put into JSON
        #note that these must match the attributes of this object EXACTLY


    def set_type(self, type: str):
        """
        Set what will prefix this' JSON output,
        allowing the program's JSON readers to
        reconvert the JSON to an object
        """
        self.type = type

    def set_user(self, user: 'AbstractCharacter'):
        """
        Sets this' user
        """
        self.user = user


    def calc_all(self):
        """
        Calculates all this' stats
        """
        for stat in self.attributes.values():
            stat.reset_boosts()
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


    def track_attr(self, attr_name: str):
        """
        adds attr_name to the list of attributes to be recorded in JSON
        """
        if attr_name not in self.track:
            if attr_name not in self.__dict__:
                raise ValueError('Key not found for ' + str(self.__dict__) + ': ' + attr_name)
            else:
                self.track.append(attr_name)


    def get_data(self) -> list:
        """
        Returns a list of strings:
        a text representation of this object.
        Each subclass may want to override this
        """
        ret = [self.type + " " + self.name + ":"]
        for k, v in self.attributes.items():
            ret.append('\t' + k + ": " + str(v.get()))

        for t in self.track:
            ret.append('\t' + t + ': ' + str(self.__dict__[t]))
        return ret


    def display_data(self):
        """
        Prints the result of self.get_data()

        Note that subclasses don't have to override this
        """
        Op.add(self.get_data())
        Op.display()


    def customize(self):
        """
        Provides a menu, so the player can customize this
        """
        done = False

        while not done and self.customization_points > 0:
            self.display_data()
            options = ["Save changes and quit"]
            can_up = []
            can_down = []
            for k, v in self.attributes.items():
                if not v.is_max():
                    can_up.append(k)
                if not v.is_min():
                    can_down.append(k)

            options.extend(can_up) #work on increase first
            options.reverse()

            up = choose("Which do you want to increase?", options)

            if up == "Save changes and quit":
                done = True
                break
            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! BREAK HERE


            options = ["Save changes and quit"]
            options.extend(can_down)
            options.reverse()

            if up in options:
                options.remove(up)

            down = choose("Which do you want to decrease?", options)

            if down == "Save changes and quit":
                done = True
                break
            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! BREAK HERE

            self.attributes[up].set_base(self.attributes[up].get_base() + 1)
            self.attributes[down].set_base(self.attributes[down].get_base() - 1)
            self.calc_all()
            self.customization_points -= 1


    def __str__(self) -> str:
        return self.name

    def get_as_json(self) -> dict:
        """
        returns a JSON representation of this object as a dictionary,
        which can be used to reconstuct this object.
        """
        serialize = self.attributes.copy()
        for t in self.track:
            serialize[t] = self.__dict__[t]

        return json.loads(json.dumps(serialize, cls=UpgradableEncoder))


class UpgradableEncoder(json.JSONEncoder):
    def default(self, obj):
        ret = None
        if isinstance(obj, Stat):
            ret = obj.get_base()
        elif isinstance(obj, AbstractUpgradable):
            ret = obj.get_as_json()
        else:
            ret = json.JSONEncoder.default(self, obj)
        return ret
