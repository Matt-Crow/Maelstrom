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
        self.team1.enemy = self.team2
        self.team2.enemy = self.team1

        while not self.isOver():
            self.team2Turn()
            self.team1Turn()

        return self.team2.isDefeated()

    def isOver(self)->bool:
        return self.team1.isDefeated() or self.team2.isDefeated()

    def team1Turn(self):
        self.teamTurn(self.team1, self.team2, self.userChoose)

    def team2Turn(self):
        self.teamTurn(self.team2, self.team1, self.aiChoose)

    def teamTurn(self, attacker, defender, chooseAction: "function(screen)"):
        if attacker.isDefeated():
            return

        msgs = []

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
        for option in attacker.active.getActiveChoices():
            screen.addOption(option)

        choice = chooseAction(screen) # this part differs between players and AI

        screen.clearBody()
        screen.clearOptions() # prevents a bug where the the next call to display didn't work
        msgs.append(choice.use())
        defender.updateMembersRem(msgs)
        screen.addSplitRow(
            attacker.getShortDisplayData(),
            defender.getShortDisplayData()
        )
        screen.addBodyRows(msgs)
        screen.display()

    def userChoose(self, screen):
        return screen.displayAndChoose("What active do you wish to use?")

    def aiChoose(self, screen):
        screen.clearOptions() # don't let user see AI's choices
        return self.team2.active.whatActive()


"""
Use these to decide which enemies to target. Should only allow user to choose
attacks that can hit anyone
"""


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
