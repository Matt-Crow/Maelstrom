"""
This module replaces the old distinction between player and AI teams
"""

from maelstrom.dataClasses.team import Team

class User:
    """
    A User simply contains a name and team.
    Future versions will also store campaign info and other choices in this
    """

    def __init__(self, name: str, team: Team):
        self.name = name
        self.team = team

    def getDisplayData(self) -> list[str]:
        return [
            f'User {self.name}',
            f'Team:',
            "\n".join(_get_detailed_team_data(self.team))
        ]

def _get_detailed_team_data(team: Team)->list[str]:
    """
    This provides a more descriptive overview of the team, detailing all of its
    members. It feels a little info-dump-y, so it feels tedious to scroll
    through. Do I want some other way of providing players with team data?
    """

    lines = [
        f'{team.name}:'
    ]
    for member in team.members:
        lines.append(member.get_display_data())

    return lines