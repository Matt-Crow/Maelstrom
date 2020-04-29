from output import Op

"""
This will replace the old AbstractUpgradable class,
sometime in the future
"""


class AbstractCustomizable(object):
    nextId = 0
    def __init__(self, name: str, customPoints=0):
        super(AbstractCustomizable, self).__init__()
        self.name = name
        self.customizationPoints = customPoints
        self.id = AbstractCustomizable.nextId
        AbstractCustomizable.nextId += 1

    def __str__(self):
        return "AbstractCustomizable#{0}: {1}".format(self.id, self.name)

    def displayData(self):
        Op.add(str(self))
        Op.display()
