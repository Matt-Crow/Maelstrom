from utilities import *

HIT_GIVEN_EVENT = 0
HIT_TAKEN_EVENT = 1
UPDATE_EVENT = 2 # should accept an AbstractCharacter as an argument

EVENT_TYPES = (HIT_GIVEN_EVENT, HIT_TAKEN_EVENT, UPDATE_EVENT)

"""
Action registers are used to
hold functions which should be
invoked whenever a specific
condition is met, such as being
hit. They should each take an
extention of AbstractEvent as
a paramter
"""
class ActionRegister:
    def __init__(self):
        self.actions = {enumType : [] for enumType in EVENT_TYPES}

    # no more duration nonsense
    def addActionListener(self, enumType, action):
        if enumType in EVENT_TYPES:
            self.actions[enumType].append(action)
        else:
            raise Exception("Unsupported event type: {0}. Must be one of {1}".format(enumType, EVENT_TYPES))

    def fire(self, enumType, event=None):
        if enumType in EVENT_TYPES:
            for action in self.actions[enumType]:
                action(event)
        else:
            raise Exception("Unsupported event type: {0}. Must be one of {1}".format(enumType, EVENT_TYPES))

    def clear(self):
        for value in self.actions.values():
            value.clear()


"""
an OnHitEvent is created during
battle whenever one character
hits another. The event is then
passed in to all of the hitter's
onHitGiven functions and all of
the hitee's onHitTaken functions
"""
class OnHitEvent:
    def __init__(self, id, hitter, hitee, hit_by, damage):
        self.id = id
        self.hitter = hitter
        self.hitee = hitee
        self.hit_by = hit_by
        self.damage = damage
