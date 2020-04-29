from output import Op

"""
This will replace the old AbstractUpgradable class,
sometime in the future
"""


class AbstractCustomizable(object):
    nextId = 0
    """
    name is used for creating the save file
    for this object.

    type is used when decoding its JSON file.
    """
    def __init__(self, name: str, type: str, customPoints=0):
        super(AbstractCustomizable, self).__init__()
        self.name = name
        self.type = type
        self.customizationPoints = customPoints
        self.id = AbstractCustomizable.nextId
        # Key: attr name, value: Stat.
        # attributes which to player can customize.
        self.customizableAttributes = {}
        # other attributes which should be written when serializing this.
        self.trackedAttributes = {}
        AbstractCustomizable.nextId += 1

    def addStat(self, stat):
        self.customizableAttributes[stat.name.lower()] = stat

    def __str__(self):
        return "AbstractCustomizable#{0}: {1}".format(self.id, self.name)

    def displayData(self):
        Op.add(str(self))
        Op.display()
