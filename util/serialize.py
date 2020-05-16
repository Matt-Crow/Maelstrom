import json
import os
from stat_classes import Stat

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

class CustomJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        ret = None
        #input(type(obj)) debug tool
        if isinstance(obj, AbstractJsonSerialable):
            ret = obj.toJsonDict()
        elif isinstance(obj, Stat):
            ret = obj.base
        else:
            ret = json.JSONEncoder.default(self, obj)
        return ret
