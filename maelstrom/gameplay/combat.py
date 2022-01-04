"""
This module handles combat gameplay. This separates the data classes from the
functions that act on their data, preventing classes from become cumbersome



Still need to implement the new attack methods at the bottom, as well as
removing the old "active character" field.

Maybe move "membersRem" into the Encounter class
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
        for option in attacker.active.getActiveChoices(0, defender.membersRem):
            screen.addOption(option)

        choice = chooseAction(screen) # this part differs between players and AI

        screen.clearBody()
        screen.clearOptions() # prevents a bug where the the next call to display didn't work

        if choice is not None: # some characters may have no valid targets
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
        return self.team2.active.bestActive(0, self.team1.membersRem)
