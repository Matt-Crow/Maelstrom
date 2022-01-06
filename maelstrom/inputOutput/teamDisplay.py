


from inputOutput.screens import Screen # old io package
from util.stringUtil import lengthOfLongest # old util package



def getTeamDisplayData(team: "Team")->"List<str>":
    """
    Used in the in-battle HUD
    """
    lines = [
        f'{team.name}'
    ]
    longestName = lengthOfLongest((member.name for member in team.membersRemaining))
    longestHp = lengthOfLongest((str(member.remHp) for member in team.membersRemaining))
    for member in team.membersRemaining:
        lines.append(f'* {member.name.ljust(longestName)}: {str(member.remHp).rjust(longestHp)} HP')

    return lines

    
def getDetailedTeamData(team: "Team")->"List<str>":
    """
    This provides a more descriptive overview of the team, detailing all of its
    members. It feels a little info-dump-y, so it feels tedious to scroll
    through. Do I want some other way of providing players with team data?
    """

    lines = [
        f'{team.name}:'
    ]
    for member in team.members:
        lines.append(member.getDisplayData())

    return lines
