from maelstrom.dataClasses.activeAbilities import in_bounds
import unittest

class TestTargettingSystem(unittest.TestCase): 
    def test_targetting_system(self):
        self.assertTrue(in_bounds([-1, 0, 1, 2], 2) == [0, 1])

if __name__ == "__main__":
    unittest.main()