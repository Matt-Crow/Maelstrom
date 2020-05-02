import json
import os

class AbstractJsonSerialable(object):
    """
    Required kwargs:
    - type : str (used for deserializing)
    """
    def __init__(self, **kwargs):
        self.type = kwargs["type"]
        self.serializedAttributes = ["type"]
        # the list of attributes this object has that should be written to this' JSON file.

    def addSerializedAttribute(self, attrName: str):
        if attrName not in self.serializedAttributes:
            if attrName not in self.__dict__:
                raise ValueError("Key \"{0}\" not found for {1}".format(attrName, str(self.__dict__)))
            else:
                self.serializedAttributes.append(attrName)

    def addSerializedAttributes(self, *attrNames: list):
        for attr in attrNames:
            self.addSerializedAttribute(attr)

    """
    returns this' attributes to serialize,
    as a json dictionary.
    Subclasses will likely want to add keys to what this returns.
    """
    def toJsonDict(self)->dict:
        return json.loads(json.dumps({attr: self.__dict__[attr] for attr in self.serializedAttributes}, cls=CustomJsonEncoder))

    """
    Converts this' data to a json file,
    then saves it to a file
    """
    def writeToFile(self, filePath: str):
        with open(filePath, "w") as file:
            file.write(json.dumps(self.toJsonDict()))

    """
    Change to class method?
    Reads a JSON file, returning
    its content as a dictionary.
    """
    @staticmethod
    def readFile(filePath: str)->dict:
        ret = {}
        with open(filePath, "r") as file:
            ret = json.loads(file.read())
        return ret


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


    @staticmethod
    def load_json(path: str) -> dict:
        """
        Change to class method?

        parses a json file to a dictionary,
        then returns the result.

        Note that this may raise a FileNotFoundError
        """
        ret = {}
        with open(path, 'rt') as file:
            ret = json.loads(file.read())
        return ret


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
        elif isinstance(obj, AbstractJsonSerialable):
            ret = obj.toJsonDict()
        else:
            ret = json.JSONEncoder.default(self, obj)
        return ret
