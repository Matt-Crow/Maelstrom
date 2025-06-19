"""
Passive abilities are attributes a character can have that trigger when a
condition is met, such as when a character is hit or reaches a certain threshold
of health
"""

from maelstrom.dataClasses.stat_classes import Boost
from maelstrom.util.random import rollPercentage
from abc import abstractmethod

class AbstractPassive:
    def __init__(self, name, description):
        """
        name should be a unique identifier
        """
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

class ThresholdPassive(AbstractPassive):
    def __init__(self, name, boost, threshold):
        """
        threshold must be a decimal number
        """
        super().__init__(
            name,
            f'{name}: Inflicts user with {boost.get_boost_text()} when at or below {int(threshold * 100)}% HP'
        )
        self.boost = boost.copy()
        self.threshold = threshold

    def copy(self):
        return ThresholdPassive(self.name, self.boost, self.threshold)

    def registerTo(self, user):
        user.event_update.add_subscriber(self.checkTrigger)

    def checkTrigger(self, updated):
        if updated.get_percent_hp_remaining() <= self.threshold * 100:
            updated.boost(self.boost.copy())

class OnHitGivenPassive(AbstractPassive):
    def __init__(self, name, boost, chance, targetsUser):
        """
        chance should be a decimal number
        """
        super().__init__(
            name,
            f'{name}: your hits have a {int(chance * 100)}% chance to inflict {"you" if targetsUser else "the target"} with {boost.get_boost_text()}'
        )
        self.boost = boost.copy()
        self.chance = chance
        self.targetsUser = targetsUser

    def copy(self):
        return OnHitGivenPassive(self.name, self.boost, self.chance, self.targetsUser)

    def registerTo(self, user):
        user.event_hit_given.add_subscriber(self.checkTrigger)

    def checkTrigger(self, onHitEvent):
        if rollPercentage(onHitEvent.hitter.get_stat_value("luck")) > 100 - self.chance * 100:
            if self.targetsUser:
                onHitEvent.hitter.boost(self.boost.copy())
            else:
                onHitEvent.hitee.boost(self.boost.copy())

class OnHitTakenPassive(AbstractPassive):
    def __init__(self, name, boost, chance, targetsUser):
        """
        chance should be a decimal number
        """
        super().__init__(
            name,
            f'{name}: hits against you have a {int(chance * 100)}% chance to inflict {"you" if targetsUser else "the attacker"} with {boost.get_boost_text()}'
        )
        self.boost = boost.copy()
        self.chance = chance
        self.targetsUser = targetsUser

    def copy(self):
        return OnHitTakenPassive(self.name, self.boost, self.chance, self.targetsUser)

    def registerTo(self, user):
        user.event_hit_taken.add_subscriber(self.checkTrigger)

    def checkTrigger(self, onHitEvent):
        if rollPercentage(onHitEvent.hitee.get_stat_value("luck")) > 100 - self.chance * 100:
            if self.targetsUser:
                onHitEvent.hitee.boost(self.boost.copy())
            else:
                onHitEvent.hitter.boost(self.boost.copy())



def getPassiveAbilityList():
    return [
        ThresholdPassive("Threshhold test", Boost("resistance", 0.5, 1), 0.25),
        OnHitGivenPassive("On Hit Given Test", Boost("luck", 0.25, 3), 0.25, True),
        OnHitTakenPassive("On Hit Taken Test", Boost("control", -0.25, 3), 0.25, False)
    ]
