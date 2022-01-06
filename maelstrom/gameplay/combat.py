"""
This module handles combat gameplay. This separates the data classes from the
functions that act on their data, preventing classes from become cumbersome
"""



from maelstrom.inputOutput.teamDisplay import getTeamDisplayData
from inputOutput.screens import Screen



class Encounter:
    """
    An encounter handles team versus team conflict.
    """
    def __init__(self, team1: "Team", team2: "Team", weather: "Weather"):
        self.team1 = team1
        self.team2 = team2
        self.weather = weather

    def resolve(self)->bool:
        """
        runs the encounter. Returns True if team1 wins
        """
        self.team1.initForBattle()
        self.team2.initForBattle()

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

    def teamTurn(self, attacker, defender, chooseAction: "function(screen, character, characterOrdinal, defenderTeam)"):
        if attacker.isDefeated():
            return

        msgs = []

        msgs.extend(attacker.updateMembersRemaining())
        self.weather.applyEffect(attacker.membersRemaining, msgs)
        msgs.extend(attacker.updateMembersRemaining())

        for memberOrdinal, member in enumerate(attacker.membersRemaining):
            options = member.getActiveChoices(memberOrdinal, defender.membersRemaining)
            if len(options) == 0:
                msgs.append(f'{member.name} has no valid targets!')
            else:
                self.characterChoose(attacker, member, memberOrdinal, defender, chooseAction, msgs)

    def characterChoose(self, attackerTeam, character, characterOrdinal, defenderTeam, chooseAction, msgs):
        screen = Screen()
        screen.setTitle(f'{character}\'s turn')
        screen.addSplitRow(
            getTeamDisplayData(attackerTeam),
            getTeamDisplayData(defenderTeam)
        )
        screen.addBodyRows(msgs)

        options = character.getActiveChoices(characterOrdinal, defenderTeam.membersRemaining)
        if len(options) == 0:
            screen.addBodyRow(f'{character.name} has no valid targets!')
        else: # let them choose their active and target
            choice = chooseAction(screen, character, characterOrdinal, defenderTeam.membersRemaining)

            screen.clearBody()
            screen.clearOptions() # prevents a bug where the screen wouldn't display
            msgs.append(choice.use())
            msgs.extend(defenderTeam.updateMembersRemaining())
            screen.addSplitRow(
                getTeamDisplayData(attackerTeam),
                getTeamDisplayData(defenderTeam)
            )
            screen.addBodyRows(msgs)
        screen.display()

    def userChoose(self, screen, character, characterOrdinal, defenderTeam):
        for option in character.getActiveChoices(characterOrdinal, defenderTeam):
            screen.addOption(option)
        return screen.displayAndChoose("What active do you wish to use?")

    def aiChoose(self, screen, character, characterOrdinal, defenderTeam):
        return character.bestActive(characterOrdinal, defenderTeam)
