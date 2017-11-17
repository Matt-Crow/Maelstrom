if __name__ == "__main__":
  print("Oops! You're running from the wrong file!")
  print("Try running Maelstrom.py instead!")
  exit()

import random # still needed for non-luck things

characters = {}
enemies = {}
passives = []
ELEMENTS = ("lightning", "rain", "hail", "wind")
STATS = ("control", "resistance", "Potency", "luck", "energy")


def get_hit_perc(lv):
  """
  Calculates how much
  damage an attack should
  do to a target at a given
  level
  """
  return 16.67 * (1 + lv * 0.05)

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
        if data[0] == "P":
          for i in data:
            if i == "P":
              continue
            else:
              self.dict_file[name]["Passives"].append(i.replace("_", " "))
        else:
          name = data[0]
          self.dict_file[name] = {"Stats": [], "Passives": []}
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
          for passive in data["Passives"]:
            member.add_passive(passive)
    return ret
  
  def update(self, team):
    self.text_to_dict()
    Dp.add(["Before:", self.dict_file])
    
    change = {}
    for member in team.team:
      change[member.name] = {"Stats": []}
      change[member.name]["Stats"] = [str(member.level), str(member.level_set), str(member.XP), str(member.stars)]
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
      
    file.write(new)
    file.close()


"""
Events
"""
class AbstractEvent(object):
  def __init__(self, id):
    self.id = id
    
  def check_trigger(self):
    pass
    
  def trip(self):
    pass

class OnHitEvent(AbstractEvent):
  """
  an OnHitEvent is created during 
  battle whenever one character 
  hits another. The event is then
  passed in to all of the hitter's
  onHitGiven functions and all of
  the hitee's onHitTaken functions
  """
  def __init__(self, id, hitter, hitee, hit_by, damage):
    self.id = id
    self.hitter = hitter
    self.hitee = hitee
    self.hit_by = hit_by
    self.damage = damage
    
  def display_data(self):
    Dp.add("OnHitEvent " + self.id)
    Dp.add(self.hitter.name + " struck " + self.hitee.name)
    Dp.add("using " + self.hit_by.name)
    Dp.add("dealing " + str(self.damage) + " damage")
    Dp.dp()

"""
Actives:
"""
class AbstractAttack(object):
  """
  The attacks all characters can use
  """
  def __init__(self, name, mult, energy_cost):
    """
    """
    self.name = name
    self.dmg_mult = mult
    
    self.damages = {}
    self.damage_distribution = {"physical":50}
    for element in ELEMENTS:
      self.damage_distribution[element] = 12.5
    
    self.miss = 0
    self.crit = 0
    self.miss_mult = 1.0
    self.crit_mult = 1.0
    self.energy_cost = energy_cost
    
    self.side_effects = []
  
  def set_damage_distributions(self, new_dist):
    """
    new_dist should be a dictionary
    """
    self.damage_distribution = new_dist
  
  def add_side_effect(self, function, chance = 100):
    self.side_effects.push({"effect": function, "chance":chance}) 
  
  def set_user(self, user):
    self.user = user
    self.distribute_damage()
  
  def init_for_battle(self):
    self.distribute_damage()
  
  def distribute_damage(self):
    total = get_hit_perc(self.user.level) * self.dmg_mult
    split_between = 0
    self.damages = {}
    for value in self.damage_distribution.values():
      split_between += value
    for type, value in self.damage_distribution.items():
      self.damages[type] = total / split_between * value
  
  def display_data(self):
    Op.add(self.name)
    for type, value in self.damages.items():
      Op.add(type + " damage: " + str(int(value)))
    Op.add("Critical hit chance: " + str(self.crit) + "%")
    Op.add("Miss chance: " + str(self.miss) + "%")
    Op.add("Critical hit multiplier: " + str(int(self.crit_mult * 100)) + "%")
    Op.add("Miss penalty: " + str(int(self.miss_mult * 100)) + "%")
    Op.dp(False)
  
  def can_use(self):
    return self.user.energy >= self.energy_cost

  def calc_MHC(self):
    """
    Used to calculate hit type
    """
    ret = 1.0
	
    if (self.miss > 0 and self.crit > 0):
      rand = roll_perc(self.user.get_stat("luck"))
      Dp.add(["rand in calc_MHC: " + str(rand), "Crit: " + str(100 - self.crit), "Miss: " + str(self.miss)])
      Dp.dp()
      if rand <= self.miss:
        Op.add("A glancing blow!")
        ret = self.miss_mult
      
      elif rand >= 100 - self.crit:
        Op.add("A critical hit!")
        ret = self.crit_mult
      
    return ret
  
  def hit(self, target):
    target.take_DMG(self.user, self)
    for side_effect in self.side_effects:
      rand = roll_perc(self.user.get_stat("luck"))
      
      Dp.add("Rolling for side effect...")
      Dp.add("Rolled: " + str(rand))
      Dp.add("Minimum to activate: " + str(side_effect["chance"]))
      Dp.dp()
      
      if rand > 100 - side_effect["chance"]:
        side_effect["effect"]()
      
  def use(self):
    self.user.lose_energy(self.energy_cost)

class ActAttack(AbstractAttack):
  def use(self):
    self.hit(self.user.team.enemy.active)
    super(ActAttack, self).use()

class MeleeAttack(ActAttack):
  def __init__(self, name, dmg, miss, crit, miss_mult, crit_mult):
    super(MeleeAttack, self).__init__(name, dmg, 0)
    self.miss = miss
    self.crit = crit
    self.miss_mult = miss_mult
    self.crit_mult = crit_mult

class AllAttack(AbstractAttack):
  def use(self):
    for member in self.user.team.enemy.members_rem:
      self.hit(member)
    super(type(self), self).use()

class AnyAttack(AbstractAttack):
  def use(self):  
    if self.user.team.AI:
      highest = 0
      best = None
      options = []
      if self.user.team.switched_in:
        m = 0.75
      else:
        m = 1.0
      
      for member in self.user.team.enemy.members_rem:
        damage = member.calc_DMG(self.user, self) * m
        if damage >= member.HP_rem:
          options.append(member)
        if damage >= highest:
          highest = damage
          best = member
      
      if len(options) >= 1:
        target_team.members_rem[random.randint(0, len(options) - 1)].take_DMG(self.user, self)
      else:
        self.hit(best)
    else:
      self.hit(choose("Who do you wish to hit?", target_team.members_rem))
    super(type(self), self).use()


"""
Passives
"""
class AbstractPassive(object):
  """
  HOW TO ADD A PASSIVE TO A CHARACTER:
  1. define the passive:
  * pas = ~~~Passive(~ ~ ~ ~ ~ ~)
  2. append the passive:
  * character.passives.append(pas)
  3. set the user:
  * pas.set_user(character)
  """
  def __init__(self, name, stat, potency, duration, targets_user = True):
    self.name = name
    self.boosted_stat = stat
    self.boost_amount = potency
    self.boost_duration = duration
    self.desc = " with a " + str(potency) + "% boost to their " + stat + " stat for " + str(duration) + " turns "
    self.targets_user = targets_user
  
  def set_user(self, user):
    self.user = user
  
  def find_target(self):
    ret = self.user
    if not self.targets_user:
      ret = self.user.team.enemy.active
    return ret
  
  def f(self):
    self.find_target().boost(self.boosted_stat, self.boost_amount, self.boost_duration, self.name)
  
  def display_data(self):
    Op.add("TODO: " + self.name + " display_data")
    Op.dp()

class Threshhold(AbstractPassive):
  """
  Automatically invoked at the end of every turn
  """
  def __init__(self, name, threshhold, stat, potency, duration):
    super(self.__class__, self).__init__(name, stat, potency, duration)
    self.threshhold = threshhold
  
  def init_for_battle(self):
    self.user.add_on_update_action(self.check_trigger)
  
  def check_trigger(self):
    Dp.add("Checking trigger for " + self.name)
    Dp.add(str(self.threshhold) + "% threshhold")
    Dp.add(str(self.user.hp_perc()) + "% user health")
    if self.user.hp_perc() <= self.threshhold:
      Dp.add("activated")
      self.f()
    Dp.dp()
  
  def display_data(self):
    Op.add(self.name + ":")
    Op.add("Inflicts user")
    Op.add(self.desc)
    Op.add("when at or below")
    Op.add(str(self.threshhold) + "% maximum Hit Points") 
    Op.dp()

class OnHitGiven(AbstractPassive):
  def __init__(self, name, chance, stat, potency, duration, targets_user = True):
    super(self.__class__, self).__init__(name, stat, potency, duration, targets_user)
    self.chance = chance
  
  def init_for_battle(self):
    self.user.add_on_hit_given_action(self.check_trigger)
  
  def check_trigger(self, onHitEvent):
    rand = roll_perc(self.user.get_stat("luck"))
    Dp.add("Checking trigger for " + self.name)
    Dp.add("Need to roll " + str(100 - self.chance) + " or higher to activate")
    Dp.add("Rolled " + str(rand))
    if rand > 100 - self.chance:
      Dp.add("activated")
      self.f()
    Dp.dp()
  
  def display_data(self):
    Op.add(self.name + ":")
    Op.add("Whenever the user strikes an opponent, ")
    Op.add("there is a " + str(self.chance) + " chance that the")
    if self.targets_user:
      Op.add("user")
    else:
      Op.add("target")
    Op.add(self.desc)
    Op.dp()

class OnHitTaken(AbstractPassive):
  def __init__(self, name, chance, stat, potency, duration, targets_user = True):
    super(self.__class__, self).__init__(name, stat, potency, duration, targets_user)
    self.chance = chance
  
  def init_for_battle(self):
    self.user.add_on_hit_taken_action(self.check_trigger)
  
  def check_trigger(self, onHitEvent):
    rand = roll_perc(self.user.get_stat("luck"))
    Dp.add("Checking trigger for " + self.name)
    Dp.add("Need to roll " + str(100 - self.chance) + " or higher to activate")
    Dp.add("Rolled " + str(rand))
    if rand > 100 - self.chance:
      Dp.add("activated")
      self.f()
    Dp.dp()
  
  def display_data(self):
    Op.add(self.name + ":")
    Op.add("Whenever the user is struck by an opponent, ")
    Op.add("there is a " + str(self.chance) + " chance that the")
    if self.targets_user:
      Op.add("user")
    else:
      Op.add("target")
    Op.add(self.desc)
    Op.dp()


"""
Poor stat, all alone :(
"""
class Stat(object):
  """
  A class used to store
  information about a stat,
  making it easier to keep 
  track of values
  """
  def __init__(self, name, base, enable_leveling = False):
    self.name = name
    self.base_value = float(base)
    self.boosts = []
    self.value = float(base)
    self.can_level_up = enable_leveling
  
  def calc(self, level):
    if not self.can_level_up:
      level = 0
    self.value = self.base_value * (1 + 0.2 * level)
  
  def boost(self, id, amount, duration):
    self.boosts.append({"id":id, "amount":amount, "duration":duration})
  
  def get(self):
    mult = 1.0
    for boost in self.boosts:
      mult += boost["amount"]
    return self.value * mult
  
  def reset_boosts(self):
    self.boosts = []
  
  def update(self):
    new_boosts = []
    for boost in self.boosts:
      """
      a stat boost with a duration
      of 1 will be checked, then
      down to 0, while a duration
      of -1 will always fail the 
      check; thus, lasting forever
      """
      if boost["duration"] != 0:
        new_boosts.append(boost)
        boost["duration"] -= 1
    self.boosts = new_boosts
  
  def display_data(self):
    Dp.add(self.name);
    Dp.add("Raw: " + str(self.base_value))
    Dp.add("Boosts:")
    for boost in self.boosts:
      Dp.add("ID: " + boost["id"])
      Dp.add("-Amount: " + str(boost["amount"]))
      Dp.add("-Duration: " + str(boost["duration"]))
    Dp.add("Calculated: " + str(self.value))
    Dp.dp()



"""
Characters
"""
class AbstractCharacter(object):
  """
  A Class containing all the info for a character
  """
  
  """
  Initializers:
  Used to 'build' the characters
  """
  def __init__(self, name, data, level):
    """
    """
    self.name = name
    self.stats = [Stat("HP", 100)]
    
    stat_num = 0
    while stat_num < 5:
      # a bit convoluted
      self.stats.append(Stat(STATS[stat_num], 20 + set_in_bounds(data[0][stat_num], -5, 5), True))
      stat_num += 1
    self.stats.append(Stat("Physical damage multiplier", 100))
    
    self.stats.append(Stat("Physical damage reduction", 100))
    
    for element in ELEMENTS:
      self.stats.append(Stat(element + " damage multiplier", 100))
      self.stats.append(Stat(element + " damage reduction", 100))
    
    self.element = data[1]
    self.level = level
    self.XP = 0
    self.level_set = 1
    
    self.attacks = [data[2]]
    self.add_default_actives()
    self.set_passives_to_defaults()
  
  #temporary
  def add_default_actives(self):
    self.attacks.append(MeleeAttack("slash", 1.0, 15, 15, 0.75, 1.5))
    self.attacks.append(MeleeAttack("jab", 0.75, 10, 40, 0.5, 2.0))
    self.attacks.append(MeleeAttack("slam", 1.35, 30, 15, 0.5, 1.35))
    for attack in self.attacks:
      attack.set_user(self)
  
  #temporary
  def set_passives_to_defaults(self):
    self.passives = []
    
    
    return
    
    
    p = Threshhold("Threshhold test", 50, "resistance", 50, 1)
    self.passives.append(p)
    p.set_user(self)
    
    o = OnHitGiven("OnHitGivenTest", 50, "control", -50, 1, False)
    self.passives.append(o)
    o.set_user(self)
    
    h = OnHitTaken("OnHitTakenTest", 50, "luck", 50, -1)
    self.passives.append(h)
    h.set_user(self)
  
  def calc_stats(self):
    """
    Calculate a character's stats
    """
    for stat in self.stats:
      stat.calc(self.level)
  
  # HP defined here
  def init_for_battle(self):
    """
    Prepare for battle!
    """
    self.reset_action_registers()
    
    for stat in self.stats:
      stat.reset_boosts()
    for attack in self.attacks:
      attack.init_for_battle()
    for passive in self.passives:
      passive.init_for_battle()
    
    self.calc_stats()
    self.HP_rem = self.get_stat("HP")
    self.energy = int(self.get_stat("energy") / 2.0)
  
  # action register class?
  def reset_action_registers(self):
    """
    Action registers are used to
    hold functions which should be
    invoked whenever a specific
    condition is met, such as being
    hit. They should each take an 
    extendtion of AbstractEvent as
    a paramter
    """
    self.on_hit_given_actions = []
    self.on_hit_taken_actions = []
    self.on_update_actions = []
  
  def add_on_hit_given_action(self, action, duration = -1):
    """
    duration is how long to check for the condition
    """
    self.on_hit_given_actions.append({"function":action, "duration":duration})
  
  def add_on_hit_taken_action(self, action, duration = -1):
    """
    duration of -1 means it lasts forever in battle
    """
    self.on_hit_taken_actions.append({"function":action, "duration":duration})
  
  def add_on_update_action(self, action, duration = -1):
    """
    """
    self.on_update_actions.append({"function":action, "duration":duration})
  
  def update_action_registers(self):
    """
    Standard decrement, check, reasign
    pattern I use all the time
    """
    def update(register):
      new = []
      for action in register:
        action["duration"] -= 1
        # don't check if negative,
        # that way I can make stuff last forever
        if action["duration"] != 0:
          new.append(action)
    update(self.on_hit_given_actions)
    update(self.on_hit_taken_actions)
    update(self.on_update_actions)
  
  """
  Data obtaining functions:
  Used to get data about a character
  """
  
  def hp_perc(self):
    """
    Returns as a value between 0 and 100
    """
    return int((float(self.HP_rem) / float(self.get_stat("HP"))) * 100.0)
  
  def get_stat(self, name):
    """
    Returns the calculated
    value of a given stat.
    If it is not found,
    notify Dp, and return -1
    """
    ret = -1
    for stat in self.stats:
      if stat.name.upper() == name.upper():
        ret = stat.get()
    
    if ret == -1:
      Dp.add("Stat not found: " + name)
      Dp.dp()
    
    return ret
  
  def display_data(self):
    """
    Print info on a character
    """
    self.calc_stats()
    Op.add("Lv. " + str(self.level) + " " + self.name)
    Op.add(self.element)
    
    Op.add("STATS:")
    for stat in STATS:
      Op.add(stat + ": " + str(int(self.get_stat(stat))))
    
    Op.add("ACTIVES:")
    for attack in self.attacks:
      Op.add("-" + attack.name)
    
    Op.add("PASSIVES:")
    for passive in self.passives:
      Op.add("-" + passive.name)
    
    Op.add(str(self.XP) + "/" + str(self.level * 10))
    Op.dp()
  
  def display_mutable_stats(self):
    for stat_name in STATS:
      Op.add(stat_name + ": " + str(int(self.get_stat(stat_name))))
    Op.dp(False)
  
  """
  Battle functions:
  Used during battle
  """
  # add ID checking to prevent doubling up
  def boost(self, name, amount, duration, id = " "):
    """
    Increase or lower stats in battle
    amount will be an integeral amount
    20 translates to 20%
    """
    mult = 1 + self.get_stat("potency") / 100
    
    found = False
    statNum = 0
    while statNum < len(self.stats) and not found:
      if self.stats[statNum].name == name:
        found = True
        self.stats[statNum].boost(id, amount * mult / 100, duration)
      statNum += 1
    if not found:
      Dp.add("STAT NOT FOUND: " + name)
      Dp.dp()
  
  def heal(self, percent):
    """
    Restores HP.
    Converts an INTEGER
    to a percentage.
    """
    mult = 1 + self.get_stat("potency") / 100
    healing = self.get_stat("HP") * (float(percent) / 100)
    self.HP_rem = self.HP_rem + healing * mult
    
    Op.add(self.name + " healed " + str(int(healing)) + " HP!")
    Op.dp()
        
    if self.HP_rem > self.get_stat("HP"):
      self.HP_rem = self.get_stat("HP")
  
  def harm(self, percent):
    mult = 1 - self.get_stat("potency") / 100
    harming = self.get_stat("HP") * (float(percent) / 100)
    self.HP_rem = int(self.HP_rem - harming * mult)
    Op.add(self.name + " took " + str(int(harming)) + " damage!")
    Op.dp()
    
  def direct_dmg(self, dmg):
    self.HP_rem -= dmg
    self.HP_rem = int(self.HP_rem)
  
  def gain_energy(self, amount):
    """
    Increase your energy.
    """
    self.energy = self.energy + amount
    
    if self.energy > self.get_stat("energy"):
      self.energy = self.get_stat("energy")
    
    self.energy = int(self.energy)
  
  def lose_energy(self, amount):
    """
    Decrease your energy
    """
    self.energy = self.energy - amount
    if self.energy < 0:
      self.energy = 0
  
  # stat.display_data in here
  def update(self):
    self.update_action_registers()
    for action in self.on_update_actions:
      action["function"]()
    
    self.gain_energy(self.get_stat("energy") * 0.15)
    for stat in self.stats:
      stat.update()
      #stat.display_data();
  
  """
  Damage calculation
  """
  def calc_DMG(self, attacker, attack_used):
    """
    MHC is not checked here so that it doesn't
    mess with AI
    """
    damage = 0
    for damage_type, value in attack_used.damages.items():
      damage += value * (attacker.get_stat(damage_type + " damage multiplier") / self.get_stat(damage_type + " damage reduction"))
    damage *= attacker.get_stat("control") / self.get_stat("resistance")
    
    if attacker.team.switched_in:
      damage = damage * 0.75
      
    return damage
  
  def take_DMG(self, attacker, attack_used):
    dmg = self.calc_DMG(attacker, attack_used)
    dmg = dmg * attack_used.calc_MHC()
    Op.add(attacker.name + " struck " + self.name)
    Op.add("for " + str(int(dmg)) + " damage")
    Op.add("using " + attack_used.name + "!")
    Op.dp()
    
    event = OnHitEvent("Attack", attacker, self, attack_used, dmg)
    event.display_data()
    
    for passive in self.on_hit_taken_actions:
      passive["function"](event)
    
    for passive in attacker.on_hit_given_actions:
      passive["function"](event)
    
    self.direct_dmg(dmg)
  
  def check_if_KOed(self):
    """
    Am I dead yet?
    """
    return self.HP_rem <= 0

class PlayerCharacter(AbstractCharacter):
  def __init__(self, name, data, level):
    super(self.__class__, self).__init__(name, data, level)
    self.attack_customization_points = 0
  
  def choose_attack(self):
    attack_options = []
    for attack in self.attacks:
      if attack.can_use():
        attack_options.append(attack)
    
    choose("What attack do you wish to use?", attack_options).use()
  
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
    self.attack_customization_points += 1
    self.calc_stats()
    self.HP_rem = self.get_stat("HP")
    self.display_data()
  
  def plus_level_set(self):
    """
    Increases your 
    level cap by 5
    """
    self.level_set = self.level_set + 1
  
  """
  Character management
  """
  def customize_attack(self, attack):
    attack.distribute_damage()
    attack.display_data()
    
    # copy the old attack data into new data
    new_data = {}
    for k, v in attack.damage_distribution.items():
      new_data[k] = v
    
    can_down = []
    
    for k, v in attack.damage_distribution.items():
      if v > 0:
        can_down.append(k)
    
    new_data[choose("Which damage stat do you want to increase by 12.5% of total damage?", new_data.keys())] += 12.5
    new_data[choose("Which damage stat do you want to decrease by 12.5%? of total damage", can_down)] -= 12.5
    attack.set_damage_distributions(new_data)
    attack.distribute_damage()
    attack.display_data()
    
    self.attack_customization_points -= 1
  
  def choose_attack_to_customize(self):
    self.customize_attack(choose("Which attack do you want to modify?", self.attacks))
  
  def customize(self):
    options = ["Quit"]
    if self.attack_customization_points > 0:
      options.append("Attack")
    
    choice = choose("What do you want to modify?", options)
    
    if choice == "Attack":
      self.choose_attack_to_customize()

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


"""
Teams
"""
class AbstractTeam(object):
  """
  Teams are used to group characters
  together so that the program knows
  who are enemies, and who are allies.
  """
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
  
  def init_active(self):
    """
    Elect a leader
    """
    self.active = self.use[0]
      
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
      member.init_for_battle()
      self.members_rem.append(member)
    self.init_active()
  
  def list_members(self):
    """
    Display the data
    of each member
    of the team
    """
    Op.add(self.name)
    Op.dp(False)
    for member in self.team:
      member.display_data()
  
  def display_data(self):
    """
    Show info for a team
    """
    Op.add(self.name)
    for member in self.members_rem:
      Op.add("* " + member.name + " " + str(int(member.HP_rem)) + "/" + str(int(member.get_stat("HP"))))
    Op.add("Currently active: " + self.active.name)
    self.active.display_mutable_stats()
    Op.add(self.active.name + "'s Energy: " + str(self.active.energy))
    Op.add("Active enemy: " + self.enemy.active.name + " " + str(int(self.enemy.active.HP_rem)) + "/" + str(int(self.enemy.active.get_stat("HP"))))
    Op.dp()
    
  def do_turn(self):
    """
    This is where stuff happens
    """
    new_members_rem = []
    for member in self.members_rem:
      if not member.check_if_KOed():
        new_members_rem.append(member)
        member.update()
      else:
        Op.add(member.name + " is out of the game!")
        Op.dp()
    self.members_rem = new_members_rem
    
    if self.active.check_if_KOed() and self.is_up():
      self.choose_switchin()
    
    if self.is_up():
      self.switched_in = False
      self.choose_action()

class PlayerTeam(AbstractTeam):
  def __init__(self, name, member):
    self.team = []
    self.name = name
    self.team.append(PlayerCharacter(member["name"], member["data"], member["level"]))
    for member in self.team:
      member.team = self
  
  """
  Choices are made using these functions
  """         
  def choose_switchin(self):
    """
    Who will fight?
    """
    choices = []
    for member in self.members_rem:
      if member != self.active:
        choices.append(member)
    
    self.switch(choose("Who do you want to bring in?", choices))
      
    Op.add(self.active.name + " up!")
    Op.dp()
                                    
  def choose_action(self):
    """
    What to do, what to do...
    """
    self.display_data()
    choices = ["Attack"]
    
    if not self.one_left():
      choices.append("Switch")
    
    if choose("What do you wish to do?", choices) == "Switch":
      self.choose_switchin()
      self.switched_in = True
    self.active.choose_attack()
  
  """
  Customization options
  """
  def customize(self):
    self.team[0].customize()
  
class EnemyTeam(AbstractTeam):
  def __init__(self, name, members):
    self.team = []
    self.name = name
    
    members = to_list(members)
    for new_member in members:
      self.team.append(EnemyCharacter(new_member["name"], new_member["level"]))
    for member in self.team:
      member.team = self
  
  """
  AI stuff
  BENCHIT NEEDS FIX
  general improvements needed
  """
  def should_switch(self):
    """
    First, check if our active can KO
    """
    if self.one_left():
      return "Attack"
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
    self.switch(self.who_switch())
      
    Op.add(self.active.name + " up!")
    Op.dp()
                                    
  def choose_action(self):
    """
    What to do, what to do...
    """
    self.display_data()
    
    choices = ["Attack"]
    
    if not self.one_left():
      choices.append("Switch")
      
    if self.should_switch() == "Switch":
      self.choose_switchin()
      self.switched_in = True
    self.active.choose_attack()



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

# BUG: adds player multiple times when played consecutively
class Battle(object):
  """
  The Battle class pits 2 teams
  against eachother, 
  initializing them
  and the weather.
  """
  def __init__(self, name, description, script, end, team_size, weather_list, rewards = None):
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
  # add random loot
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
    """
    if not winner.AI:
      self.final_act.print_story()
      for reward in self.rewards:
        if reward == None:
          continue
        reward.give(winner)
    """
  
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
      if team.__class__ == PlayerTeam:
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

from utilities import *
from navigate import Story