from utilities import *
"""
Events
"""
class AbstractEvent(object):
    def __init__(self, id):
        self.id = id
        
    def check_trigger(self):
        pass
        
    def trip(self):
        pass

class OnHitEvent(AbstractEvent):
    """
    an OnHitEvent is created during 
    battle whenever one character 
    hits another. The event is then
    passed in to all of the hitter's
    onHitGiven functions and all of
    the hitee's onHitTaken functions
    """
    def __init__(self, id, hitter, hitee, hit_by, damage):
        self.id = id
        self.hitter = hitter
        self.hitee = hitee
        self.hit_by = hit_by
        self.damage = damage
        
    def displayData(self):
        Dp.add("OnHitEvent " + self.id)
        Dp.add(self.hitter.name + " struck " + self.hitee.name)
        Dp.add("using " + self.hit_by.name)
        Dp.add("dealing " + str(self.damage) + " damage")
        Dp.dp()