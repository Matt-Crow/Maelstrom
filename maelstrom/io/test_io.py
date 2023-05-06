from unittest import TestCase
from maelstrom.io.chooser import Chooser
from maelstrom.io.input import ListInputChannel
from maelstrom.io.output import ListOutputChannel

class TestIO(TestCase):
    def test_read_int(self):
        sut = ListInputChannel(['42'])
        actual = sut.read_int()
        self.assertEqual(42, actual)
    
    def test_read_int_with_invalid(self):
        sut = ListInputChannel(['foo', 'bar', '3'])
        actual = sut.read_int()
        self.assertEqual(3, actual)
    
    def test_read_int_all_invalid(self):
        sut = ListInputChannel(['foo', 'bar', 'baz', 'qux'])
        with self.assertRaises(ValueError):
            sut.read_int()
    
    def test_chooser(self):
        input_channel = ListInputChannel(['foo', 'bar', '2'])
        output_channel = ListOutputChannel()
        sut = Chooser(input_channel, output_channel)
        actual = sut.choose('prompt', ['a', 'b', 'c'])
        self.assertEqual('b', actual)
    
    def test_chooser_invalid(self):
        input_channel = ListInputChannel(['foo', 'bar', 'baz', 'qux'])
        output_channel = ListOutputChannel()
        sut = Chooser(input_channel, output_channel)
        with self.assertRaises(IndexError):
            sut.choose('prompt', ['a', 'b', 'c'])