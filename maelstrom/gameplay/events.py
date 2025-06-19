from typing import Callable

class EventPublisher[T]:
    """Allows subscribers to listen for something."""

    def __init__(self) -> None:
        self._subscribers = []
    
    def add_subscriber(self, subscriber: Callable[[T], None]):
        self._subscribers.append(subscriber)
    
    def clear_subscribers(self):
        self._subscribers.clear()

    def publish_event(self, event: T):
        for subscriber in self._subscribers:
            subscriber(event)


class OnHitEvent:
    def __init__(self, id, hitter, hitee, hit_by, damage):
        self.id = id
        self.hitter = hitter
        self.hitee = hitee
        self.hit_by = hit_by
        self.damage = damage
