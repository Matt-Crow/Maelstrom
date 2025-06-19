import unittest

from maelstrom.gameplay.events import EventPublisher

class TestEvents(unittest.TestCase):
    def test(self):
        sut = EventPublisher()
        subscriber = SubscriberDummy()
        sut.add_subscriber(subscriber.handle_event)

        sut.publish_event(42)

        self.assertIn(42, subscriber.history)

class SubscriberDummy:
    def __init__(self) -> None:
        self.history = []
    
    def handle_event(self, value: int):
        self.history.append(value)