from character import AbstractCharacter
import json

#this file is for management purposes ONLY.
#use it if the data in files gets corrupted or needs to be reset
#TODO: add CLI for creating enemies

def save_base():
    """
    Saves the base character to its proper file under the files directory
    """
    with open('files/base_character.json', 'wt') as file:
        file.write(json.dumps(AbstractCharacter.create_default_player().get_as_json()))


def generate_enemies():
    """
    Copies the data from files/base_character,
    then edits the data to make enemies,
    finally, it saves their data under files/enemy_characters

    replace this with maelscript once I get that implemented
    """

    def set_all_attr_to(c: 'AbstractCharacter', val: int):
        """
        Removes the repeated code for min and max
        """
        for k in c.attributes.keys():
            c.set_base(k, val)
        for active in c.attacks:
            for k in active.attributes.keys():
                active.set_base(k, val)
        for passive in c.passives:
            for k in passive.attributes.keys():
                passive.set_base(k, val)
        for item in c.equipped_items:
            for k in item.attributes.keys():
                item.set_base(k, val)

    base = AbstractCharacter.read_default_player()

    maxj = base.get_as_json()
    minj = base.get_as_json()

    maxj['type'] = 'EnemyCharacter'
    minj['type'] = 'EnemyCharacter'

    max = AbstractCharacter.read_json(maxj)
    min = AbstractCharacter.read_json(minj)

    max.name = 'MAX'
    min.name = 'MIN'

    set_all_attr_to(max, 10)
    set_all_attr_to(min, -10)

    with open('files/enemy_characters/MAX.json', 'wt') as file:
        file.write(json.dumps(max.get_as_json()))
    with open('files/enemy_characters/MIN.json', 'wt') as file:
        file.write(json.dumps(min.get_as_json()))

    lj = base.get_as_json()
    lj['name'] = 'Lightning Entity'
    lj['element'] = 'lightning'

    lightning = AbstractCharacter.read_json(lj)

    for k, v in {
        'control' : 10,
        'resistance' : -10,
        'lightning damage multiplier' : 10,
        'wind damage reduction' : -10
        }.items():
        lightning.set_base(k, v)
