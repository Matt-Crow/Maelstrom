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

    max.save()
    min.save()


    lightning = AbstractCharacter.read_json({
        'name' : 'Lightning Entity',
        'type' : 'EnemyCharacter',
        'element' : 'lightning',
        'energy' : {
            'type': 'Stat',
            'base': 10,
            'name': 'energy'
        },
        'resistance' : {
            'type': 'Stat',
            'base': -10,
            'name': 'resistance'
        },
        'lightning damage multiplier' : {
            'type': 'Stat',
            'base': 10,
            'name': 'lightning damage multiplier'
        },
        'wind damage reduction' : {
            'type': 'Stat',
            'base': -10,
            'name': 'wind damage reduction'
        },
        'attacks' : [
            {
                'name' : 'Plasma Bolt',
                'type' : 'AbstractActive',
                'lightning damage weight' : {
                    'type': 'Stat',
                    'base': 10,
                    'name': 'lightning damage weight'
                },
                'miss chance' : {
                    'type': 'Stat',
                    'base': -10,
                    'name': 'miss chance'
                }
            }
        ]
    })
    lightning.add_default_actives()
    lightning.add_default_passives()
    lightning.save()


    rain = AbstractCharacter.read_json({
        'name' : 'Rain Entity',
        'type' : 'EnemyCharacter',
        'element' : 'rain',
        'potency' : 10,
        'control' : -10,
        'rain damage multiplier' : 10,
        'lightning damage reduction' : -10,
        'attacks' : [
            {
                'name' : 'Eroding Rain',
                'type' : 'AbstractActive',
                'cleave' : 10,
                'damage multiplier' : -10
            }
        ]
    })
    rain.add_default_actives()
    rain.add_default_passives()
    rain.save()


    hail = AbstractCharacter.read_json({
        'name' : 'Hail Entity',
        'type' : 'EnemyCharacter',
        'element' : 'hail',
        'resistance' : 10,
        'luck' : -10,
        'hail damage multiplier' : 10,
        'rain damage reduction' : -10,
        'attacks' : [
            {
                'name' : 'Icicle Jab',
                'type' : 'AbstractActive',
                'crit chance' : 10,
                'cleave' : -10
            }
        ]
    })
    hail.add_default_actives()
    hail.add_default_passives()
    hail.save()


    wind = AbstractCharacter.read_json({
        'name' : 'Wind Entity',
        'type' : 'EnemyCharacter',
        'element' : 'wind',
        'luck' : 10,
        'potency' : -10,
        'wind damage multiplier' : 10,
        'hail damage reduction' : -10,
        'attacks' : [
            {
                'name' : 'Tornado',
                'type' : 'AbstractActive',
                'crit mult' : 10,
                'miss mult' : -10
            }
        ]
    })
    wind.add_default_actives()
    wind.add_default_passives()
    wind.save()


    stone = AbstractCharacter.read_json({
        'name' : 'Stone Soldier',
        'type' : 'EnemyCharacter',
        'element' : 'stone',
        'control' : 5,
        'resistance' : 10,
        'luck' : -5,
        'energy' : -5,
        'potency' : -5
    })
    stone.add_default_actives()
    stone.add_default_passives()
    stone.save()
