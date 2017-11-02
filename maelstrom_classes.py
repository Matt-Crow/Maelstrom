if __name__ == "__main__":
  print("Oops! You're running from the wrong file!")
  print("Try running Maelstrom.py instead!")
  exit()

import random

characters = {}
enemies = {}
passives = []
ELEMENTS = ["lightning", "rain", "hail", "wind"]


def load():
  ret = Team("Test team", ({"name": "Alexandre", "level": 1}, 
  {"name": "Rene", "level": 1}, 
  {"name": "Ian", "level": 1}, 
  {"name": "Viktor", "level": 1}), 
  False)
  
  should_load = choose("Do you want to load from a save file?", ("Yes", "No"))
  
  if should_load == "Yes":
    file = Savefile("player_data.txt")
    ret = file.upload_team()
    
  return ret

# need to comment this
# ARRRGGG work here
class Savefile(object):
  def __init__(self, file):
    self.file = file
  
  def text_to_dict(self):
    self.dict_file = {}
    file_read = open(self.file, "r")
    for line in file_read:
      if line == " ":
        continue
      line = line.split("!")
      Dp.add(["Line.split:", line])
      for item in line:
        data = item.split()
        Dp.add(["Data.split:", data])
        if data[0] == "W":
          self.dict_file[name]["Weapon"] = [data[1], data[2], data[3], data[4], data[5]]
        elif data[0] == "P":
          for i in data:
            if i == "P":
              continue
            else:
              self.dict_file[name]["Passives"].append(i.replace("_", " "))
        else:
          name = data[0]
          self.dict_file[name] = {"Stats": [], "Weapon": [], "Passives": []}
      	  self.dict_file[name]["Stats"] = [data[1], data[2], data[3], data[4]]
    Dp.add(["Dict file:", self.dict_file])
    Dp.dp()
  
  def upload_team(self):
    self.text_to_dict()
    members = []
    for name, data in self.dict_file.items():
      Dp.add(["Name:", name, "Data:", data])
      members.append({"name": name, "level": int(data["Stats"][0])})
    Dp.add(["Members:", members])
    ret = Team("Player Team", members, False)
    Dp.dp()
    
    for member in ret.team:
      for name, data in self.dict_file.items():
        if member.name == name:
          member.level_set = int(data["Stats"][1])
          member.XP = int(data["Stats"][2])
          member.stars = int(data["Stats"][3])
          member.equip(Weapon(data["Weapon"][0], int(data["Weapon"][1]), int(data["Weapon"][2]), int(data["Weapon"][3]), int(data["Weapon"][4])))
          for passive in data["Passives"]:
            member.add_passive(passive)
    return ret
  
  def update(self, team):
    self.text_to_dict()
    Dp.add(["Before:", self.dict_file])
    
    change = {}
    for member in team.team:
      change[member.name] = {"Stats": [], "Weapon": []}
      change[member.name]["Stats"] = [str(member.level), str(member.level_set), str(member.XP), str(member.stars)]
      change[member.name]["Weapon"] = [(member.weapon.name), str(member.weapon.base_miss), str(member.weapon.base_crit), str(member.weapon.base_miss_mult), str(member.weapon.base_crit_mult)]
    self.dict_file = change
    Dp.add(["After:", self.dict_file])
    Dp.dp()
    file = open("player_data.txt", "w")
    new = " "
    for member, data in change.items():
      new = new + member + " "
      new = new + data["Stats"][0] + " "
      new = new + data["Stats"][1] + " "
      new = new + data["Stats"][2] + " "
      new = new + data["Stats"][3] + " "
      new = new + data["Weapon"][0] + " "
      new = new + data["Weapon"][1] + " "
      new = new + data["Weapon"][2] + " "
      new = new + data["Weapon"][3] + " "
      new = new + data["Weapon"][4] + "\n"
      
    file.write(new)
    file.close()

# TODO: add hit principle to damage, add side effects
class AbstractAttack(object):
  """
  The regular attacks all characters can use
  as well as characters' exclusive Specials
  """
  def __init__(self, name, energy_cost = 0):
    """
    """
    self.name = name
    
    self.damages = {}
    self.damage_distribution = {"physical":4}
    for element in ELEMENTS:
      self.damage_distribution[element] = 1
    
    self.distribute_damage()
      
    self.energy_cost = energy_cost  
  
  def distribute_damage(self):
    total = 16.0 #redo with HPrince
    split_between = 0
    self.damages = {}
    for value in self.damage_distribution.values():
      split_between += value
    for type, value in self.damage_distribution.items():
      self.damages[type] = total / split_between * value
  
  def can_use(self, user):
    return user.energy >= self.energy_cost
      
  def use(self, user):
    user.lose_energy(self.energy_cost)

class ActAttack(AbstractAttack):
  def use(self, user):
    user.team.enemy.active.take_DMG(user, self)
    super(type(self), self).use(user)

class AllAttack(AbstractAttack):
  def use(self, user):
    for member in user.team.enemy.members_rem:
      member.take_DMG(user, self)
    super(type(self), self).use(user)

class AnyAttack(AbstractAttack):
  def use(self, user):  
    if user.team.AI:
      highest = 0
      best = None
      options = []
      if user.team.switched_in:
        m = 0.75
      else:
        m = 1.0
      
      for member in user.team.enemy.members_rem:
        damage = member.calc_DMG(user, self) * m
        if damage >= member.HP_rem:
          options.append(member)
        if damage >= highest:
          highest = damage
          best = member
      
      if len(options) >= 1:
        target_team.members_rem[random.randint(0, len(options) - 1)].take_DMG(user, self)
      else:
        best.take_DMG(user, self)
    else:
      choose("Who do you wish to hit?", target_team.members_rem).take_DMG(user, self)
    super(type(self), self).use(user)

# working here
# not fully implemented
class Passive(object):
  def __init__(self, name, type, x, self_target, stat, potency, duration):
    self.name = name
    # move this?
    self.type = type
    # value used for calculations
    self.x = x
    self.self_target = self_target
    
    self.stat = stat
    self.potency = potency
    self.duration = duration
  
  def get_target(self, user):
    if not self.self_target:
      return user.team.enemy.active
    return user
  
  def activate(self, user):
    self.get_target(user).boost(self.stat, self.potency, self.duration)

class Threshhold(Passive):
  def check_trigger(self, user):
    if self.get_target(user).hp_perc() <= self.x:
      self.activate(user)
    Dp.add(["Current HP: " + str(self.get_target(user).hp_perc()), "Threshhold: " + str(self.x)])
    Dp.dp()
  
  def display_data(self):
    Op.add(self.name + ":")
    
    if self.self_target:
      Op.add("Inflicts user with a")
    else:
      Op.add("Inflicts target with a")
      
    Op.add(str(int(self.potency * 100)) + "% boost")
    Op.add("to their " + self.stat + " stat")
    Op.add("when they are at or below")
    Op.add(str(int(self.x * 100)) + "% HP.")
    
    Op.dp()

class OnHit(Passive):
  def check_trigger(self, user):
    r = random.randint(1, 100)
    Dp.add(["Random: " + str(r), "Minimum: " + str(self.x)])
    Dp.dp()
    if r <= self.x * 100:
      self.activate(user)
      
  def display_data(self):
    Op.add([self.name + ":", "Whenever the user"])
    
    if self.self_target:
      Op.add("is struck by an enemy melee attack")
    else:
      Op.add("strikes an enemy with a melee attack")
      
    Op.add("there is a " + str(int(self.x * 100)) + "% chance")
    
    Op.add("the target will recieve a " + str(int(self.potency * 100)) + "% boost")
    Op.add("to their " + self.stat + " stat")
    Op.add("for " + str(self.duration) + " turns.")
    
    Op.dp()

class Weapon(object):
  """
  """
  def __init__(self, name, miss, crit, miss_m, crit_m):
    self.name = name
    stats = [miss, crit, miss_m, crit_m]
    stat_num = 0  
    while stat_num < len(stats):
      stats[stat_num] = set_in_bounds(stats[stat_num], -3, 3)
      stat_num += 1
    self.miss = 20 + stats[0] * 5
    self.crit = 20 + stats[1] * 5
    self.miss_mult = 0.8 - stats[2] * 0.05
    self.crit_mult = 1.25 + stats[3] * 0.05
    
    # Used in save file
    self.base_miss = miss
    self.base_crit = crit
    self.base_miss_mult = miss_m
    self.base_crit_mult = crit_m
    
  def display_data(self):
    Op.add(self.name + " data:")
    Op.add("Miss chance: " + str(self.miss) + "%")
    Op.add("Crit chance: " + str(self.crit) + "%")
    Op.add("Miss multiplier: " + str(self.miss_mult) + "%")
    Op.add("Crit multiplier: " + str(self.crit_mult) + "%")
    Op.dp()
  
  def calc_MHC(self):
    """
    Used to calculate hit type
    """
    rand = random.randint(1, 100)
    ret = 1.0
    Dp.add(["rand in calc_MHC: " + str(rand), "Crit: " + str(100 - self.crit), "Miss: " + str(self.miss)])
    Dp.dp()
    if rand <= self.miss:
      Op.add("A glancing blow!")
      ret = self.miss_mult
    
    elif rand >= 100 - self.crit:
      Op.add("A critical hit!")
      ret = self.crit_mult
    
    return ret
      
  def give(self, team):
    team.arsenal.append(self)
    Dp.add(team.arsenal)
    Dp.dp()

class Stat(object):
  """
  A class used to store
  information about a stat,
  making it easier to keep 
  track of values
  """
  def __init__(self, name, base):
    self.name = name
    self.base_value = float(base)
    self.boosts = []
    self.value = float(base)
  
  def calc(level):
    self.value = self.base_value * 0.2 * level
  
  def boost(id, amount, duration):
    self.boosts.append({"id":id, "amount":amount, "duration":duration})
  
  def get():
    mult = 1.0
    for boost in self.boosts:
      mult += boost["amount"]
    return self.value * mult
  
  def update():
    new_boosts = []
    for boost in self.boosts:
      boost["duration"] -= 1
      if boost["duration"] > 0:
        new_boosts.append(boost)
    self.boosts = new_boosts


# extend to Hero and Enemy
class Character(object):
  """
  A Class containing all the info for a character
  """
  
  """
  Initializers:
  Used to 'build' the characters
  """
  
  def __init__(self, name, level):
    """
    base stats: (def ratio, res ratio, con ratio)
    """
    self.name = name
    if name in characters:
      data = characters[name]
    elif name in enemies:
      data = enemies[name]
    else:
      data = ((0, 0, 0), "stone", None)
    self.base_stats = data[0]
    self.element = data[1]
    self.special = data[2]
    self.level = level
    self.XP = 0
    self.level_set = 1
    self.stars = 0
    self.attacks = [slash, jab, slam]
    self.attacks.append(data[2])
    self.weapon = Weapon("Default", 0, 0, 0, 0)
    self.passives = [Threshhold("Test", "Threshhold", 0.5, "user", "STR", 0.2, 1), OnHit("Test", "OnHit", 0.5, "enemy", "STR", -0.2, 3)]
    
    self.base_dmg_mults = {"physical":1.0}
    self.base_dmg_reductions = {"physical":0.0}
    for element in ELEMENTS:
      self.base_dmg_mults[element] = 1.0
      self.base_dmg_reductions[element] = 0.0
    self.calc_dmg_modifiers()
    
  def calc_stats(self):
    """
    Calculate a character's stats
    """
    s = []
    for stat in self.base_stats:
      s.append(stat)
    stat_num = 0
    while stat_num < len(s):
      s[stat_num] = set_in_bounds(s[stat_num], -5, 5)
      stat_num += 1
    
    def_mult = 1.0 + s[0] * 0.15
    off_mult = 1.0 - s[0] * 0.15
    
    base_HP = def_mult * 100
    
    RESRAT = 0.5 + s[1] * 0.05
    HPRAT = 1.0 - RESRAT
    
    # default is 0.5, so 20 base
    base_res = RESRAT * def_mult * 40
    base_hp = HPRAT * def_mult * 40
    
    # offensive stats
    CONRAT = 0.5 + s[2] * 0.05
    STRRAT = 1.0 - CONRAT
     
    # once again, default is 0.5
    base_con = CONRAT * off_mult * 40
    base_str = STRRAT * off_mult * 40
    
    self.stats = dict()
        
    self.stats["HP"] = base_HP * (1 + self.level * 0.1)
    self.stats["RES"] = base_res * (1 + self.level * 0.2) 
    self.stats["STR"] = base_str * (1 + self.level * 0.2) 
    self.stats["CON"] = base_con * (1 + self.level * 0.2) 
  
  # move to stats. Stat class? store boosts, base, calculated?
  def calc_dmg_modifiers(self):
    self.dmg_mults = {}
    self.dmg_reductions = {}
    
    for type, value in self.base_dmg_mults.items():
      self.dmg_mults[type] = value
    for type, value in self.base_dmg_reductions.items():
      self.dmg_reductions[type] = value
  
  def reset_boosts(self):
    """
    Set your 
    boosts 
    as a dict
    """
    self.boosts = {"CON": [], "STR": [], "RES": []}
  
  def init_for_battle(self):
    """
    Prepare for battle!
    """
    self.reset_boosts()
    self.calc_stats()
    self.calc_dmg_modifiers()
    self.HP_rem = self.get_stat("HP")
    self.energy = 0
    self.burn = [0, 0]
  
  def equip(self, weapon):
    self.weapon = weapon
  
  def add_passive(self, name):
    from maelstrom import passives
    for passive in passives:
      if passive.name == name:
        self.passives.append(passive)
  
  """
  Data obtaining functions:
  Used to get data about a character
  """
  
  def hp_perc(self):
    return float(self.HP_rem) / float(self.get_stat("HP"))
  
  def get_stat(self, stat):
    ret = -1
    if stat not in self.stats:
      Dp.add("Stat not found: " + stat)
      Dp.dp()
    else:
      ret = int(self.stats[stat] * self.get_boost(stat))
    return ret
  
  # move to stats
  def get_dmg_mult(self, stat):
    ret = -1
    for type, value in self.dmg_mults.items():
      if type == stat:
        ret = value
    
    if ret == -1:
      Dp.add("Stat not found: " + stat)
      Dp.dp()
    
    return ret
  
  def get_dmg_reduction(self, stat):
    ret = -1
    for type, value in self.dmg_reductions.items():
      if type == stat:
        ret = value
    
    if ret == -1:
      Dp.add("Stat not found: " + stat)
      Dp.dp()
    
    return ret    
  
  def display_data(self):
    """
    Print info on a character
    """
    self.calc_stats()
    Op.add("Lv. " + str(self.level) + " " + self.name)
    Op.add(self.element)
    Op.add("HP: " + str(int(self.stats["HP"])))
    Op.add("STR:" + str(int(self.stats["STR"])))
    Op.add("CON:" + str(int(self.stats["CON"])))
    Op.add("RES:" + str(int(self.stats["RES"])))
    for attack in self.attacks:
      Op.add("-" + attack.name)
    Op.add(str(self.XP) + "/" + str(self.level * 10))
    Op.dp()
    self.weapon.display_data()
    for passive in self.passives:
      passive.display_data()
  
  """
  Battle functions:
  Used during battle
  """
  def boost(self, stat, amount, duration):
    """
    Increase or lower stats in battle
    """
    self.boosts[stat].append({"potency": amount, "duration": duration})
  
  def get_boost(self, stat):
    """
    Returns stat boost
    """
    ret = 1
    try:
      for boost in self.boosts[stat]:
        ret += boost["potency"]
    except:
      pass
    return ret
  
  def update_boosts(self):
    new_boosts = dict()
    for stat in self.boosts.keys():
      new_boosts[stat] = []
      for boost in self.boosts[stat]:
        if boost["duration"] != 0:
          new_boosts[stat].append({"potency": boost["potency"], "duration": boost["duration"] - 1})
    self.boosts = new_boosts
    Dp.add(self.name + "'s boosts:")
    for boost_type in self.boosts.keys():
      Dp.add(boost_type + ": ")
      for boost in self.boosts[boost_type]:
        Dp.add("-------------")
        Dp.add("-Duration: " + str(boost["duration"]))
        Dp.add("-Potency: " + str(boost["potency"]))
    Dp.dp()
  
  def heal(self, percent):
    """
    Restores HP.
    Converts an INTEGER
    to a percentage.
    """
    healing = self.get_stat("HP") * (float(percent) / 100)
    self.HP_rem = int(self.HP_rem + healing)
    
    Op.add(self.name + " healed " + str(int(healing)) + " HP!")
    Op.dp()
        
    if self.HP_rem > self.get_stat("HP"):
      self.HP_rem = self.get_stat("HP")
  
  def harm(self, percent):
    harming = self.get_stat("HP") * (float(percent) / 100)
    self.HP_rem = int(self.HP_rem - harming)
    Op.add(self.name + " took " + str(int(harming)) + " damage!")
    Op.dp()
    
  def direct_dmg(self, dmg):
    self.HP_rem -= int(dmg)
  
  def gain_energy(self, amount):
    """
    Increase your energy.
    """
    self.energy = self.energy + amount
    
    if self.energy > 20:
      self.energy = 20
  
  def lose_energy(self, amount):
    """
    Decrease your energy
    """
    self.energy = self.energy - amount
    if self.energy < 0:
      self.energy = 0
  
  """
  AI stuff
  """
  def best_attack(self):
    best = None
    highest_dmg = 0
    Dp.add("----------")
    for attack in self.attacks:
      if not attack.can_use(self):
        continue
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
    
    for attack in self.attacks:
      if not attack.can_use(self) or not type(attack) == type(AllAttack("test")):
        continue
      
      koes = 0
      for member in self.team.enemy.members_rem:
        if member.calc_DMG(self, attack) * sw >= member.HP_rem:
          koes += 1
      if koes >= 2:
        return attack
    
    """
    Can you get a KO?
    """
    can_ko = []
    
    for attack in self.attacks:
      if not attack.can_use(self):
        continue
      if self.team.enemy.active.calc_DMG(self, attack) * sw >= self.team.enemy.active.HP_rem:
        can_ko.append(attack)
      
    if len(can_ko) == 1:
      return can_ko[0]
    """
    If you cannot KO...
    """
    return self.best_attack()
    
  def choose_attack(self):
    """
    How doth thee strike?
    """
    if not self.team.AI:
      attack_options = []
      for attack in self.attacks:
        if attack.can_use(self):
          attack_options.append(attack)
      
      choice = choose("What attack do you wish to use?", attack_options)
      
    else:
      Dp.add("AI is choosing attack...")
      Dp.dp()
      choice = self.what_attack()
    
    choice.use(self)
    if choice.energy_cost == 0:
      for passive in self.passives:
        if passive.type == "OnHit":
          passive.check_trigger(self)
  
  """
  Damage calculation
  """
  
  def armor_threshhold(self):
    return (255.0 - self.get_stat("RES")) / 255.0
  
  def in_threshhold(self):
    return self.hp_perc() >= self.armor_threshhold()
  
  def reduction(self):
    return 1.0 - float(self.get_stat("RES")) / 255
  
  def calc_DMG(self, attacker, attack_used):
    damage = 0
    for damage_type, value in attack_used.damages.items():
      damage += value * (attacker.get_dmg_mult(damage_type) - self.get_dmg_reduction(damage_type))
    damage *= float(attacker.get_stat("STR")) / self.get_stat("RES")
    
    if self.in_threshhold():
      damage *= self.reduction()
    
    if attacker.team.switched_in:
      damage = damage * 0.75
      
    return int(damage)
  
  def take_DMG(self, attacker, attack_used):
    dmg = self.calc_DMG(attacker, attack_used)
    Dp.add([str(self.hp_perc() * 100) + "% HP: ", str(self.armor_threshhold() * 100) + " threshhold"])
    Dp.dp()
    if self.in_threshhold():
      Op.add(self.name + "'s armor protects him/her for damage!")
    
    dmg = dmg * self.weapon.calc_MHC()
    Op.add(attacker.name + " struck " + self.name)
    Op.add("for " + str(int(dmg)) + " damage")
    Op.add("using " + attack_used.name + "!")
    Op.dp()
    self.direct_dmg(dmg)
    self.gain_energy(3)
  
  def check_if_burned(self, attacker):
    r = random.randint(1, 255)
    if r <= attacker.get_stat("CON"):
      self.burn = [attacker.get_stat("CON") / 5, 3]
  
  def update_burn(self):
    if self.burn[1] == 0:
      return False
    self.direct_dmg(self.burn[0])
    self.burn[1] -= 1
    print(self.name + " took " + str(int(self.burn[0])) + " damage from his/her Elemental Burn!")
  
  def check_if_KOed(self):
    """
    Am I dead yet?
    """
    return self.HP_rem <= 0
  
  """
  Post-battle actions:
  Occur after battle
  """        
  def gain_XP(self, amount):
    """
    Give experience.
    Caps at the most XP required for a battle
    (Can't level up twice after one battle)
    """
    if self.team.AI:
      return
    
    self.XP = self.XP + amount
    if self.XP >= self.level * 10: 
      if self.level < self.level_set * 5:
        Op.add(self.name + " leveled up!")
        self.level_up()
      else:
        Op.add(self.name + " is being held back... perhaps a special item will help?")
      Op.dp()
  
  def level_up(self):
    """
    Increases level
    """
    self.XP = 0
    self.level += 1
    self.calc_stats()
    self.HP_rem = self.get_stat("HP")
    self.display_data()
  
  def plus_level_set(self):
    """
    Increases your 
    level cap by 5
    """
    self.level_set = self.level_set + 1
    
  def unlock_passive(self, pas):
    self.passives.append(choose("Choose a passive:", pas))

class Contract(object):
  def __init__(self, comes_with):
    """
    A contract is used to hire a
    new character, or boost an old
    one.
    """
    self.name = "Contract"
    self.poss = []
    comes_with = to_list(comes_with)
    if comes_with[0] == None:
      Dp.add("No set characters in contract.")
      Dp.dp()
    else:
      for character in comes_with:
        self.poss.append(character)
    
    poss = []
    for key in characters.keys():
      poss.append(key)
    size = len(self.poss)
    while size < 4:
      num = random.randint(1, len(poss) - 1)
      if poss[num] in self.poss:
        continue
      self.poss.append(poss[num])
      size += 1
  
  def use(self):
    """
    Ask the player if they want
    a hint, then let them choose
    a character.
    RETURNS THE ANSWER
    DOES NOT CHANGE THE PLAYER'S TEAM
    """
    Op.add("*Recruiting*")
    Op.dp()
    char = []
    for member in self.poss:
      char.append(Character(member, 1))
    
    for member in char:
      member.calc_stats()
    
    pick_or_hint = choose("Do you want a hint before choosing?", ("Yes", "No"))
    if pick_or_hint == "Yes":
      hint = choose("What do you want to see?", ("HP", "RES", "CON", "STR", "Element"))
      marks = "?"
      for member in char:
        hints = {
          "HP" : member.get_stat("HP"), 
          "RES" : member.get_stat("RES"),
          "CON" : member.get_stat("CON"),
          "STR" : member.get_stat("STR"),
          "Element" : member.element
        }
        Op.add(marks + ": " + str(hints[hint]))
        marks = marks + "?"
      Op.dp()
                    
    new = choose("Who do you want to hire?", ("?", "??", "???", "????"))
    return {"name": self.poss[len(new) - 1], "level": 1}

# extend to player and enemy teams
class Team(object):
  """
  Teams are used to group characters
  together so that the program knows
  who are enemies, and who are allies.
  """
  def __init__(self, name, members, AI = False):
    self.team = []
    self.name = name
    self.AI = AI
    self.arsenal = []
    self.contracts = []
    
    members = to_list(members)
    for new_member in members:
      self.team.append(Character(new_member["name"], new_member["level"]))
    for member in self.team:
      member.team = self
      
  def add_member(self, new_member):
    """
    Add a member to a team.
    """
    for member in self.team:
      if new_member["name"] == member.name:
        member.stars += 1
        Op.add(member.name + "'s stats were boosted!")
        Op.dp()
        member.init_for_battle()
        member.display_data()
        return False
    self.team.append(Character(new_member["name"], new_member["level"]))
    Op.add(new_member["name"] + " joined " + self.name + "!")
    Op.dp()
    self.team[-1].team = self
    self.team[-1].init_for_battle()
    self.team[-1].display_data()
    
  def find_enemy(self, teams):
    """
    Take a list of teams 
    (from Battle), and
    return the one that 
    is not self.
    """
    for team in teams:
      if team != self:
        return team
  
  # balance this later
  def xp_given(self):
    """
    How much xp will be given
    once this team is
    defeated.
    """
    xp = 0
    for member in self.use:
      xp += member.level * 10
    return xp / len(self.use)
  
  def is_up(self):
    """
    Use to see if your team still exists
    """
    return len(self.members_rem) != 0
  
  def one_left(self):
    """
    Detects when you have only one member left
    """
    return len(self.members_rem) == 1
   
  def knock_out(self, member):
    """
    Delete a warrior
    from members_rem
    """
    self.members_rem.remove(member)
  
  def init_active(self):
    """
    Elect a leader
    """
    self.active = self.use[0]
    if not self.AI:
      self.active = choose("Who do you want to lead with?", self.use)
      
  def switch(self, member):
    """
    You're up!
    """
    self.active = member
  
  def initialize(self):
    """
    Ready the troops!
    """
    self.members_rem = []
    for member in self.use:
      member.calc_stats()
      member.init_for_battle()
      self.members_rem.append(member)
    self.init_active()
  
  def display_data(self):
    """
    Show info for a team
    """
    Op.add(self.name)
    Op.dp(False)
    for member in self.team:
      member.display_data()
    
  """
  AI stuff
  BENCHIT NEEDS FIX
  """
  def should_switch(self):
    """
    First, check if our active can KO
    """
    if self.enemy.active.calc_DMG(self.active, self.active.best_attack()) >= self.enemy.active.HP_rem:
      return "Attack"
    """
    # check if your active can benchhit
    if self.active.special.act_any_all != "act":
      for member in self.enemy.members_rem:
        if member.calc_DMG(self.active, self.active.special) >= member.HP_rem and self.active.can_spec():
          if debug:
            print(self.active.name + " can KO " + member.name + " with " + self.active.special.name)
           return "Attack"
    """
    """
    Second, check if an ally can KO 
    """
    for member in self.members_rem:
      if self.enemy.active.calc_DMG(member, member.best_attack()) * 0.75 >= self.enemy.active.HP_rem:
        return "Switch"
    
    # Default
    return "Attack"
    
  # comment   
  def who_switch(self):
    """
    Used to help the AI
    decide who to switch in
    """
    
    """
    Can anyone KO?
    """
    can_ko = []
    for member in self.members_rem:
      if self.enemy.active.calc_DMG(member, member.best_attack()) * 0.75 >= self.enemy.active.HP_rem:
        can_ko.append(member)
    
    for member in can_ko:
      Dp.dd(member.name)
    
    Dp.dd("can KO")
    Dp.dp()
    
    """
    If one person can KO,
    bring them in.
    If nobody can,
    change nothing.
    If someone can KO,
    only use them.
    """
    if len(can_ko) == 1:
      return can_ko[0]
    elif len(can_ko) == 0:
      array = self.members_rem
    else:
      array = can_ko
        
    rand = random.randint(0, len(array) - 1)
    return array[rand]  
  
  """
  Choices are made using these functions
  """         
  def choose_switchin(self):
    """
    Who will fight?
    """
    
    if self.one_left():
      self.switch(self.members_rem[0])
      return
    
    choices = []
    for member in self.members_rem:
      if member != self.active:
        choices.append(member)
    
    if not self.AI:
      switch_for = choose("Who do you want to bring in?", choices)
    else:
      Dp.add("AI is deciding...")
      Dp.dp()
      switch_for = self.who_switch()
    
    self.switch(switch_for)
      
    Op.add(self.active.name + " up!")
    Op.dp()
                                    
  def choose_action(self):
    """
    What to do, what to do...
    """
    Op.add(self.name)
    for member in self.members_rem:
      Op.add("* " + member.name + " " + str(member.HP_rem) + "/" + str(member.get_stat("HP")) + " " + member.element)
        
    Op.add("Currently active: " + self.active.name)
    Op.add(self.active.name + "'s Energy: " + str(self.active.energy))
    Op.add("Active enemy: " + self.enemy.active.name + " " + str(self.enemy.active.HP_rem) + "/" + str(self.enemy.active.get_stat("HP")) + " " + self.enemy.active.element)
    
    Op.dp()
    
    choices = ["Attack"]
    
    if not self.one_left():
      choices.append("Switch")
    
    if not self.AI:
      attack_switch = choose("What do you wish to do?", choices)
    else:
      if len(choices) == 1:
        attack_switch = "Attack"
      else:
        Dp.add("AI is deciding if it should switch...")
        attack_switch = self.should_switch()
        Dp.add(attack_switch)
        Dp.dp()
      
    if attack_switch == "Switch":
      self.choose_switchin()
      self.switched_in = True
    self.active.choose_attack()
  
  # check passive triggers    
  def do_turn(self):
    """
    This is where stuff happens
    """
    new_members_rem = []
    for member in self.members_rem:
      member.update_burn()
      if not member.check_if_KOed():
        new_members_rem.append(member)
      else:
        Op.add(member.name + " is out of the game!")
        Op.dp()
    self.members_rem = new_members_rem
    
    if self.active.check_if_KOed() and self.is_up():
      self.choose_switchin()
    
    if self.is_up():
      self.switched_in = False
      for member in self.members_rem:
        for passive in member.passives:
          if passive.type == "Threshhold":
            passive.check_trigger(member)
        member.update_boosts()
      self.choose_action()

class Weather(object):
  """
  This is what makes Maelstrom unique!
  Weather provides in-battle effects
  that alter the stats of characters
  """
  def __init__(self, type, intensity, msg):
    """
    The type determines what sort of effect will
    be applied to all participants in a battle.
    The intensity is how potent the effect will be.
    The msg is what text will show to help
    the player determine the weather.
    """
    self.type = type
    self.intensity = intensity
    self.msg = msg
      
  def do_effect(self, affected):
    """
    Apply stat changes 
    to a team
    """
    
    if self.type == "Lightning":
      for person in affected:
        person.gain_energy(int(self.intensity/20))
        
    if self.type == "Wind":
      for person in affected:
        person.boost("STR", self.intensity/100, 3)
    
    if self.type == "Hail":
      for person in affected:
        person.take_dmg(self.intensity)
    
    if self.type == "Rain":
      for person in affected:
        person.heal(self.intensity)
           
  def disp_msg(self):
    """
    Print a message showing
    the weather condition
    """
    Op.add(self.msg)
    Op.dp()

class Battle(object):
  """
  The Battle class pits 2 teams
  against eachother, 
  initializing them
  and the weather.
  """
  def __init__(self, name, description, script, end, team_size, weather_list, rewards):
    """
    Maximum team size,
    Weather should be improved
    """
    self.teams = []
    self.name = name
    self.description = description
    self.script = Story(script)
    self.final_act = Story(end)
    self.team_size = team_size
    self.forecast = to_list(weather_list)
    self.rewards = to_list(rewards)
  
  def display_data(self):
    Op.add([self.name, self.description])
    
    for member in self.teams[0].use:
      Op.add("* " + member.name + " LV " + str(member.level) + " " + member.element)
    Op.dp(False)
  
  def load_team(self, team):
    """
    Add a team 
    to the battle
    """
    self.teams.append(team)
    
    if len(team.team) > self.team_size:
      Op.add("Select which " + str(self.team_size) + " members you wish to use:")
      Op.dp(False)
      num = self.team_size
      team.use = []
      roster = []
      for member in team.team:
        roster.append(member)
      
      while num > 0:
        add = choose("Select member to add:", roster)
        
        for member in team.team:
          if add == member:
            team.use.append(member)
            roster.remove(member)
            num = num - 1
    else:
      team.use = team.team
  # stuff down here
  # add random weapon
  def check_winner(self):
    """
    Runs when one
    teams loses all
    members.
    """
    for team in self.teams:
      if team.is_up():
        winner = team
    Op.add(winner.name + " won!")
    Op.dp()
    if not winner.AI:
      self.final_act.print_story()
      for reward in self.rewards:
        if reward == None:
          continue
        reward.give(winner)
  
  def begin(self):
    """
    Prepare both teams
    for the match.
    """
    self.script.print_story()
    
    for team in self.teams:
      team.initialize()
      team.enemy = team.find_enemy(self.teams)
      Op.add(team.name)
      
      for member in team.use:
        member.display_data()
      if self.forecast[0] == None:
        self.weather = Weather(None, 0, "The land is seized by an undying calm...")
      else:
        if len(self.forecast) == 1:
          num = 0
        else:
          num = random.randrange(0, len(self.forecast) - 1)
        self.weather = self.forecast[num]
      self.weather.disp_msg()
  
  def end(self):
    """
    The stuff that takes place after battle
    """
    for team in self.teams:
      for member in team.use:
        xp = team.enemy.xp_given()
        member.gain_XP(xp)
                  
  def play(self):
    """
    Used to start
    the battle
    """
    self.begin()
    while self.teams[0].is_up() and self.teams[1].is_up():
      for team in self.teams:
        if team.is_up():
          self.weather.do_effect(team.members_rem)
          team.do_turn()
        # this check is needed if the 
        #first team beats the second one
        if not team.is_up():
          break      
    self.check_winner()
    self.end()

no_eff = (0, 0, 0)
act_ene = ("enemy", "act")
        
slash = ActAttack("slash")
jab = ActAttack("jab")
slam = ActAttack("slam")

attacks = (slash, jab, slam)

from utilities import *
from navigate import Story
#from maelstrom import do_MHC, debug