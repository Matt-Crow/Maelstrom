from maelstrom.dataClasses.team import Team

class User:
    """
    A User simply contains a name and team.
    Future versions will also store campaign info and other choices in this
    """

    def __init__(self, name: str, team: Team):
        self._name = name
        self._team = team

    @property
    def name(self) -> str:
        return self._name

    @property
    def team(self) -> Team:
        return self._team

    def get_display_data(self) -> list[str]:
        lines = [
            f"User {self._name}",
            "Party:"
        ]
        lines.extend(_get_detailed_team_data(self._team))
        return lines


def _get_detailed_team_data(team: Team) -> list[str]:
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