import json
import os

"""
A JSONable is any object that can be stored as a json file.
Maelstrom uses json files to store most of the data used by the program.
"""

class Jsonable(object):
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


    def get_as_json(self) -> dict:
        """
        returns this' attributes to serialize,
        as a json dictionary.
        Subclasses will likely want to add keys to what this returns.
        """
        return json.loads(json.dumps({attr: self.__dict__[attr] for attr in self.to_serialize}, cls=CustomJsonEncoder))
        
        #return {attr: self.__dict__[attr] for attr in self.to_serialize}


    def save(self):
        """
        Converts this' data to a json file,
        then saves it to its directory, if one was given
        """
        try:
            with open(self.get_file_path(), 'wt') as file:
                file.write(json.dumps(self.get_as_json()))
        except Error as err:
            print(err) #want the warning to get through


    def get_file_path(self) -> str:
        """
        Returns the path to this' save file
        """
        if self.directory is None:
            raise AttributeError('No save directory was given for class ' + str(self.__class__))
        return self.directory + os.sep + self.name.replace(' ', '_').lower() + '.json'


class CustomJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        ret = None
        if callable(getattr(obj, 'get_as_json', None)):
            ret = obj.get_as_json()
        else:
            ret = json.JSONEncoder.default(self, obj)
        return ret

