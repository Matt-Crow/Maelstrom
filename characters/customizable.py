from serialize import AbstractJsonSerialable
from stat_classes import Stat
from utilities import choose
from abc import abstractmethod
from inputOutput.screens import SimplerGameScreen

class AbstractCustomizable(AbstractJsonSerialable):
    nextId = 0
    """
    Required kwargs:
    - type : str
    - name : str
    - customizationPoints : int (defaults to 0)
    - stats : dict{ str : int } this currently must be handled by subclasses
    """
    def __init__(self, **kwargs):
        super(AbstractCustomizable, self).__init__(**kwargs)
        self.name = kwargs["name"]
        self.type = kwargs["type"]
        self.customizationPoints = kwargs.get("customizationPoints", 0)
        self.id = AbstractCustomizable.nextId
        # Key: attr name, value: Stat.
        # attributes which to player can customize.
        self.stats = {}
        #for k, v in kwargs["stats"].items():
        #    self.addStat(k, v)
        AbstractCustomizable.nextId += 1
        self.user = None
        self.addSerializedAttributes(
            "name",
            "customizationPoints",
            "stats"
        )

    #def addStat(self, name, base):
    #    self.stats[name.lower()] = Stat(name, base)
    def addStat(self, stat):
        self.stats[stat.name.lower()] = stat

    """
    Re-sets a stat's base calculation value
    """
    def setStatBase(self, statName: str, newBase: int):
        self.stats[statName.lower()].set_base(newBase)

    def getStatValue(self, statName: str)->float:
        return self.stats[statName.lower()].get()

    def setUser(self, user):
        self.user = user

    def __str__(self):
        return self.name

    # more or less a replacement for getDisplayData()
    def getStatDisplayList(self)->list:
        ret = ["{0}'s stats:".format(self.name)]
        for k, v in self.stats.items():
            ret.append("\t{0}: {1}".format(k, str(v.get())))
        return ret

    """
    Provides a menu, so the player can customize this
    """
    def customizeMenu(self):
        done = False
        screen = SimplerGameScreen()
        screen.setTitle(f'Cusomizing {self.name}')
        while not done and self.customizationPoints > 0:
            screen.addBodyRows(self.getStatDisplayList())
            screen.display()
            exit = "Save changes and exit"
            options = [exit]
            canIncrease = []
            canDecrease = []
            for statName, stat in self.stats.items():
                if not stat.is_max():
                    canIncrease.append(statName)
                if not stat.is_min():
                    canDecrease.append(statName)
            options.extend(canIncrease) # choose stat to increase first
            options.reverse()

            increaseMe = choose("Which stat do you want to increase?", options)
            if increaseMe == exit:
                done = True
            else:
                options = [exit]
                for statName in canDecrease:
                    if statName != increaseMe:
                        options.append(statName)
                options.reverse()

                decreaseMe = choose("Which stat do you want to decrease?", options)
                if decreaseMe == exit:
                    done = True
                else:
                    self.setStatBase(increaseMe, self.stats[increaseMe].get_base() + 1)
                    self.setStatBase(decreaseMe, self.stats[decreaseMe].get_base() - 1)
                    self.calcStats()
                    self.customizationPoints -= 1
                    screen.clearBody()

    """
    Subclasses should override this method to return a textual description of
    themself
    """
    @abstractmethod
    def getDisplayData(self)->str:
        pass

    """
    Calculates all this' stats
    """
    def calcStats(self):
        for stat in self.stats.values():
            stat.reset_boosts()
            stat.calc()
