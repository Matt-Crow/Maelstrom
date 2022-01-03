"""
This module handles combat gameplay. This separates the data classes from the
functions that act on their data, preventing classes from become cumbersome
"""



from inputOutput.screens import Screen



class Encounter:
    """
    An encounter handles team versus team conflict.
    """
    def __init__(self, team1: "AbstractTeam", team2: "AbstractTeam", weather: "Weather"):
        self.team1 = team1
        self.team2 = team2
        self.weather = weather

    def resolve(self)->bool:
        """
        runs the encounter. Returns True if team1 wins
        """
        self.team1.initForBattle()
        self.team2.initForBattle()

        # TODO: do I need to set enemy_team properties?

        while not self.isOver():
            self.team2Turn()
            self.team1Turn()

        return self.team2.isDefeated()

    def isOver(self)->bool:
        return self.team1.isDefeated() or self.team2.isDefeated()

    def team1Turn(self):
        msgs = []
        screen = self.teamTurn(self.team1, self.team2, msgs)
        for option in self.team1.active.getActiveChoices():
            screen.addOption(option)
        active = screen.displayAndChoose("What active do you wish to use?");
        screen.addBodyRow(active.use())
        newMsgs = []
        self.team2.updateMembersRem(newMsgs)
        screen.addBodyRows(newMsgs)
        screen.display()

    def team2Turn(self):
        msgs = []
        screen = self.teamTurn(self.team2, self.team1, msgs)
        #TODO here

    def teamTurn(self, attacker, defender, msgs):
        """
        applies weather effects and sets up screen. Still needs to choose action
        """

        attacker.updateMembersRem(msgs)
        self.weather.applyEffect(attacker.membersRem, msgs)
        attacker.updateMembersRem(msgs)

        screen = Screen()
        screen.setTitle(f'{attacker.name}\'s turn')
        screen.addSplitRow(
            attacker.getShortDisplayData(),
            defender.getShortDisplayData()
        )
        screen.addBodyRows(msgs)

        return screen




def getActiveTargets(attackerOrdinal: int, targetTeam: "List<AbstractCharacter>")->"List<AbstractCharacter>":
    """
    'active' enemies are those across from the attacker and the enemy
    immediately below that. This gives a slight advantage to the 1 in a 1 vs 2,
    as both enemies cannot attack them at the same time

    O-X
     \X
    """
    options = []
    if attackerOrdinal < len(targetTeam):
        options.append(targetTeam[attackerOrdinal])
    if attackerOrdinal + 1 < len(targetTeam):
        options.append(targetTeam[attackerOrdinal + 1])
    return options

def getCleaveTargets(attackerOrdinal: int, targetTeam: "List<AbstractCharacter>")->"List<AbstractCharacter>":
    """
    enemies are 'cleaveable' (for want of a better word) if they are no more
    than 1 array slot away from the enemy across from the attacker
     /X
    O-X
     \X
    """
    options = getActiveTargets(attackerOrdinal, targetTeam)
    if attackerOrdinal - 1 >= 0:
        options.insert(0, targetTeam[attackerOrdinal - 1])
    return options

def getDistantTargets(attackerOrdinal: int, targetTeam: "List<AbstractCharacter>")->"List<AbstractCharacter>":
    """
    the union of distant targets and cleave targets is all enemies, with no
    overlap
    """
    notTargets = getCleaveTargets(attackerOrdinal, targetTeam)
    return [member for member in targetTeam if member not in notTargets]

def testTargettingSystem():
    targetTeam = [0, 1, 2, 3]

    assert getActiveTargets(0, targetTeam) == [0, 1]
    assert getActiveTargets(1, targetTeam) == [1, 2]
    assert getActiveTargets(2, targetTeam) == [2, 3]
    assert getActiveTargets(3, targetTeam) == [3]
    assert getActiveTargets(4, targetTeam) == []

    assert getCleaveTargets(0, targetTeam) == [0, 1]
    assert getCleaveTargets(1, targetTeam) == [0, 1, 2]
    assert getCleaveTargets(2, targetTeam) == [1, 2, 3]
    assert getCleaveTargets(3, targetTeam) == [2, 3]
    assert getCleaveTargets(4, targetTeam) == [3]

    assert getDistantTargets(0, targetTeam) == [2, 3]
    assert getDistantTargets(1, targetTeam) == [3]
    assert getDistantTargets(2, targetTeam) == [0]
    assert getDistantTargets(3, targetTeam) == [0, 1]
    assert getDistantTargets(4, targetTeam) == [0, 1, 2]

    print("done testing targetting system")
