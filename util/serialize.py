import json
import os

"""
A JSONable is any object that can be stored as a json file.
Maelstrom uses json files to store most of the data used by the program.
"""

class JsonAble(object):
    def __init__(self, name: str):
        """
        name is used for creating the save file
        for this object.

        type is used when decoding its JSON file.
        """
        self.name = name
        self.type = 'JsonAble'
        self.directory = None

        self.to_serialize = ['name', 'type'] #the list of attributes that need to be serialized.
        #note that these must match this object's attribute names exactly.


    def set_type(self, type: str):
        """
        Set what will prefix this' JSON output,
        allowing the program's JSON readers to
        reconvert the JSON to an object
        """
        self.type = type


    def track_attr(self, attr_name: str):
        """
        adds attr_name to the list of attributes to be recorded in JSON
        """
        if attr_name not in self.to_serialize:
            if attr_name not in self.__dict__:
                raise ValueError('Key not found for ' + str(self.__dict__) + ': ' + attr_name)
            else:
                self.to_serialize.append(attr_name)


    def set_save_directory(self, dir: str):
        """
        Set the directory this' data should be saved to
        """
        self.directory = dir


    def save(self):
        """
        Converts this' data to a json file,
        then saves it to its directory, if one was given
        """
        if self.directory is None:
            raise Error('No save directory was given for class ' + str(self.__class__))
        try:
            with open(self.directory + os.sep + self.name.replace(' ', '_').lower() + '.json', 'wt') as file:
                file.write(json.dumps(self.get_as_json()))
        except Error as err:
            raise(err) #want the warning to get through


def decode_json(json: dict) -> object:
    pass
