"""
This module handles combat gameplay. This separates the data classes from the
functions that act on their data, preventing classes from become cumbersome
"""



from maelstrom.inputOutput.teamDisplay import getTeamDisplayData

from battle.events import OnHitEvent, HIT_GIVEN_EVENT, HIT_TAKEN_EVENT
from maelstrom.inputOutput.output import debug
from maelstrom.inputOutput.screens import Screen
import functools



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
            options = getActiveChoices(member, memberOrdinal, defender.membersRemaining)
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

        options = getActiveChoices(character, characterOrdinal, defenderTeam.membersRemaining)
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
        for option in getActiveChoices(character, characterOrdinal, defenderTeam):
            screen.addOption(option)
        return screen.displayAndChoose("What active do you wish to use?")

    def aiChoose(self, screen, character, characterOrdinal, defenderTeam):
        choices = getActiveChoices(character, characterOrdinal, defenderTeam)
        if len(choices) == 0:
            return None

        best = choices[0]
        bestDmg = 0
        debug("-" * 10)
        for choice in choices:
            if choice.totalDamage > bestDmg:
                best = choice
                bestDmg = choice.totalDamage
            debug(f'Damage with {choice}: {choice.totalDamage}')
        debug("-" * 10)

        return best

def getActiveChoices(character: "Character", ordinal: int, targetTeam: "List<Character>")->"List<ActiveChoice>":
    useableActives = [active for active in character.actives if active.canUse(character, ordinal, targetTeam)]
    choices = []
    for active in useableActives:
        targetOptions = active.getTargetOptions(ordinal, targetTeam)
        choices.extend([ActiveChoice(active, character, ordinal, targets) for targets in targetOptions])
    return choices

def dmgAtLv(lv)->int:
    return int(16.67 * (1 + lv * 0.05))
    
def resolveAttack(attacker, target, activeUsed)->str:
    dmg = calcDmgTaken(attacker, target, activeUsed)
    hitType = activeUsed.randomHitType(attacker)
    dmg = int(dmg * hitType.multiplier)

    event = OnHitEvent("Attack", attacker, target, activeUsed, dmg)

    target.fireActionListeners(HIT_TAKEN_EVENT, event)
    attacker.fireActionListeners(HIT_GIVEN_EVENT, event)
    target.takeDmg(dmg)

    return f'{hitType.message}{attacker.name} struck {target.name} for {dmg} damage using {activeUsed.name}!'

def calcDmgTaken(attacker, target, activeUsed):
    """
    MHC is not checked here so that it doesn't
    mess with AI
    """
    return dmgAtLv(attacker.level) * activeUsed.damageMult * attacker.getStatValue("control") / target.getStatValue("resistance")

class ActiveChoice:
    """
    command design pattern
    """

    def __init__(self, active, user, userOrdinal, targets):
        self.active = active
        self.user = user
        self.userOrdinal = userOrdinal
        self.targets = targets
        self.msg = f'{active.name}->{", ".join([target.name for target in targets])}'
        self.totalDamage = functools.reduce(lambda total, next: total + next, [
            calcDmgTaken(user, target, active) for target in targets
        ])

    def __str__(self):
        return self.msg

    def use(self)->str:
        """
        todo: change this to inoke active.use
        """
        self.user.loseEnergy(self.active.cost)
        msgs = []
        for target in self.targets:
            msgs.append(resolveAttack(self.user, target, self.active))
        return "\n".join(msgs)
