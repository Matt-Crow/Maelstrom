from character import AbstractCharacter
from enemies import enemies
from utilities import Dp


class EnemyCharacter(AbstractCharacter):
    def __init__(self, name, level):
        super(self.__class__, self).__init__(name, enemies[name], level)

    """
    AI stuff
    """
    def best_attack(self):
        best = self.attacks[0]
        highest_dmg = 0
        Dp.add("----------")
        for attack in self.attacks:
            if attack.can_use():
                dmg = self.team.enemy.active.calc_DMG(self, attack)
                if dmg > highest_dmg:
                    best = attack
                    highest_dmg = dmg
                Dp.add("Damge with " + attack.name + ": " + str(dmg))
        Dp.add("----------")
        Dp.dp()
        return best

    def what_attack(self):
        """
        Used to help the AI
        choose what attack
        to use
        """
        if self.team.switched_in:
            sw = 0.75
        else:
            sw = 1.0

        """
        Can you get multiple KOes?
        """
        """
        for attack in self.attacks:
            if not attack.can_use(self) or not type(attack) == type(AllAttack("test", 0)):
                continue
            koes = 0
            for member in self.team.enemy.members_rem:
                if member.calc_DMG(self, attack) * sw >= member.HP_rem:
                    koes += 1
            if koes >= 2:
                return attack
        """
        """
        Can you get a KO?
        """
        can_ko = []
        for attack in self.attacks:
            if attack.can_use():
                if self.team.enemy.active.calc_DMG(self, attack) * sw >= self.team.enemy.active.HP_rem:
                    can_ko.append(attack)

        if len(can_ko) == 1:
            return can_ko[0]
        """
        If you cannot KO...
        """
        return self.best_attack()

    def choose_attack(self):
        self.what_attack().use()
