from maelstrom.dataClasses.activeAbilities import getActiveTargets, getCleaveTargets, getDistantTargets
import unittest

class TestTargettingSystem(unittest.TestCase): 
    def test_targetting_system(self):
        targetTeam = [0, 1, 2, 3]

        self.assertTrue(getActiveTargets(0, targetTeam) == [0, 1])
        self.assertTrue(getActiveTargets(1, targetTeam) == [1, 2])
        self.assertTrue(getActiveTargets(2, targetTeam) == [2, 3])
        self.assertTrue(getActiveTargets(3, targetTeam) == [3])
        self.assertTrue(getActiveTargets(4, targetTeam) == [])

        self.assertTrue(getCleaveTargets(0, targetTeam) == [0, 1])
        self.assertTrue(getCleaveTargets(1, targetTeam) == [0, 1, 2])
        self.assertTrue(getCleaveTargets(2, targetTeam) == [1, 2, 3])
        self.assertTrue(getCleaveTargets(3, targetTeam) == [2, 3])
        self.assertTrue(getCleaveTargets(4, targetTeam) == [3])

        self.assertTrue(getDistantTargets(0, targetTeam) == [2, 3])
        self.assertTrue(getDistantTargets(1, targetTeam) == [3])
        self.assertTrue(getDistantTargets(2, targetTeam) == [0])
        self.assertTrue(getDistantTargets(3, targetTeam) == [0, 1])
        self.assertTrue(getDistantTargets(4, targetTeam) == [0, 1, 2])

        print("done testing targetting system")

if __name__ == "__main__":
    unittest.main()