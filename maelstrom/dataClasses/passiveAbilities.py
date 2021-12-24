"""
Passive abilities are attributes a character can have that trigger when a
condition is met, such as when a character is hit or reaches a certain threshold
of health
"""



from util.serialize import AbstractJsonSerialable
from battle.events import HIT_GIVEN_EVENT, HIT_TAKEN_EVENT, UPDATE_EVENT
from abc import abstractmethod



class AbstractPassive(AbstractJsonSerialable):
    def __init__(self, name, description):
        """
        name should be a unique identifier
        """
        super().__init__(type="Passive")
        self.name = name
        self.description = description

    @abstractmethod
    def copy(self):
        pass

    @abstractmethod
    def registerTo(self, user):
        """
        This method should add listeners to the given user and reset this
        object's internal state
        """
        pass

    def toJson(self): # override default method
        return self.name



class ThresholdPassive(AbstractPassive):
    def __init__(self, name, boost, threshold):
        """
        threshold must be a decimal number
        """
        super().__init__(
            name,
            f'{name}: Inflicts user with {boost.getDisplayData()} when at or below {threshold * 100}% HP'
        )
        self.boost = boost.copy()
        self.threshold = threshold

    def copy(self):
        return ThresholdPassive(self.name, self.boost, self.threshold)

    def registerTo(self, user):
        user.addActionListener(UPDATE_EVENT, self.checkTrigger)

    def checkTrigger(self, updated):
        if updated.getHpPerc() <= self.threshold * 100:
            updated.boost(self.boost.copy())
