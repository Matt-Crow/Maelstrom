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
    """
    base = AbstractCharacter.read_default_player()

    maxj = base.get_as_json()
    maxj['type'] = 'EnemyCharacter'

    max = AbstractCharacter.read_json(maxj)
    max.name = 'MAX'
    for k in max.attributes.keys():
        max.set_base(k, 10)

    with open('files/enemy_characters/MAX.json', 'wt') as file:
        file.write(json.dumps(max.get_as_json()))
