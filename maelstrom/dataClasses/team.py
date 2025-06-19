from maelstrom.dataClasses.character import Character

class Team:
    """
    stores and manages Characters
    """

    def __init__(self, name: str, members: list[Character]):
        self._name = name
        self._members = []
        self._members_remaining = []
        for member in members:
            member.team = self
            self._members.append(member)
            self._members_remaining.append(member)

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def members(self) -> list[Character]:
        """All members in the party, KOed or otherwise."""
        return self._members
    
    @property
    def members_remaining(self) -> list[Character]:
        """Members of the party who have not been KOed."""
        return self._members_remaining

    def __str__(self):
        return self._name

    def get_xp_given(self) -> int:
        """provides how much XP this Team provides when encountered"""
        total_level = sum([m.level for m in self._members]) 
        return int(10 * total_level / len(self._members))

    def init_for_battle(self):
        """
        this method must be called at the start of each Battle
        """
        self._members_remaining.clear()
        for member in self._members: # can't use lambda with "each" here
            member.init_for_battle()
            self._members_remaining.append(member)
        self.update_members_remaining() # updates ordinals

    def is_defeated(self) -> bool:
        return len(self._members_remaining) == 0

    def update_members_remaining(self) -> list[str]:
        messages = []

        new_members_remaining = []
        next_ordinal = 0 # records which index of the array each member is in
        for member in self._members_remaining:
            if member.is_koed():
                messages.append(f'{member.name} is out of the game!')
            else:
                new_members_remaining.append(member)
                member.ordinal = next_ordinal
                next_ordinal += 1
                member.update()
        self._members_remaining = new_members_remaining

        return messages
