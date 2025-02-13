from maelstrom.dataClasses.elements import *

HIT_GIVEN_EVENT = 0
HIT_TAKEN_EVENT = 1
UPDATE_EVENT = 2 # should accept an Character as an argument

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
        self.actions = {enum_type : [] for enum_type in EVENT_TYPES}

    # no more duration nonsense
    def add_event_listener(self, enum_type, action):
        if enum_type in EVENT_TYPES:
            self.actions[enum_type].append(action)
        else:
            raise Exception("Unsupported event type: {0}. Must be one of {1}".format(enum_type, EVENT_TYPES))

    def fire(self, enum_type, event=None):
        if enum_type in EVENT_TYPES:
            for action in self.actions[enum_type]:
                action(event)
        else:
            raise Exception("Unsupported event type: {0}. Must be one of {1}".format(enum_type, EVENT_TYPES))

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
