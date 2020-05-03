from character import AbstractCharacter
import json



#this file is for management purposes ONLY.
#use it if the data in files gets corrupted or needs to be reset

def save_base():
    """
    Saves the base character to its proper file under the files directory
    """
    with open('files/base_character.json', 'wt') as file:
        file.write(json.dumps(AbstractCharacter.createDefaultPlayer().get_as_json()))


"""
Generates the default data for enemies,
and outputs it to the enemy directory.
"""
def generateEnemies():
    lightning = EnemyCharacter(
        name="Lightning Entity",
        element="lightning",
        stats={
            "energy" : 10,
            "resistance" : -10
        }
    )
    lightning.displayData()
    #lightning.save()

    rain = EnemyCharacter(
        name="Rain Entity",
        element="rain",
        stats={
            "potency" : 10,
            "control" : -10
        }
    )
    rain.displayData()
    #rain.save()

    hail = EnemyCharacter(
        name="Hail Entity",
        element = "hail",
        stats={
            "resistance" : 10,
            "luck" : -10
        }
    )
    hail.displayData()
    #hail.save()

    wind = EnemyCharacter(
        name="Wind Entity",
        element = "wind"
        stats={
            "luck" : 10,
            "potency" : -10
        }
    )
    wind.displayData()
    #wind.save()


    stone = AbstractCharacter.read_json({
        'name' : 'Stone Soldier',
        'type' : 'EnemyCharacter',
        'element' : 'stone',
        'control' : {
            'type': 'Stat',
            'base': 5,
            'name': 'control'
        },
        'resistance' : {
            'type': 'Stat',
            'base': 10,
            'name': 'resistance'
        },
        'luck' : {
            'type': 'Stat',
            'base': -5,
            'name': 'luck'
        },
        'energy' : {
            'type': 'Stat',
            'base': -5,
            'name': 'energy'
        },
        'potency' : {
            'type': 'Stat',
            'base': -5,
            'name': 'potency'
        }
    })
    stone.add_default_actives()
    stone.addPassives()
    stone.save()
