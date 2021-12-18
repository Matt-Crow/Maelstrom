"""
Since many of the objects created by the program must persist across gameplay
sessions, this module allows them to be serialized as JSON, then stored to a
file, from whence they can later be loaded.
"""
"""
This file provides the utilities that handle the conversion of JSON files to
objects within the program. In this way, the process of creating objects is
decoupled from the objects themselves.

Will need to split into file loaders and JSON decoders, as those fulfill
different tasks
"""


import json
import os.path
import abc
from fileSystem import formatFileName, unFormatFileName, getJsonFileList



class AbstractJsonSerialable:
    """
    handles the serialization of objects within the
    program as JSON objects.

    Another class or function should handle writing to a file, as not every
    individual JSON object must be written to a file.
    """
    def __init__(self, **kwargs):
        """
        Required kwargs:
        - type : str (used for deserializing)
        """
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
    def toJson(self)->dict:
        return json.loads(json.dumps({attr: self.__dict__[attr] for attr in self.serializedAttributes}, cls=CustomJsonEncoder))

    """
    Converts this' data to a json file,
    then saves it to a file
    """
    def writeToFile(self, filePath: str):
        with open(filePath, "w") as file:
            file.write(json.dumps(self.toJson()))



class CustomJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        ret = None
        if isinstance(obj, AbstractJsonSerialable):
            ret = obj.toJson()
        else:
            ret = json.JSONEncoder.default(self, obj)
        return ret



class AbstractJsonLoader(object):
    def __init__(self, dirPath: str):
        """
        dirPath is relative to the project root
            this may change if I add app data folders instead of storing in the
            project folder
        """
        self.dirPath = os.path.abspath(os.path.join(*dirPath.split(".")))

    def getOptions(self)->"List<str>":
        """
        returns a list of all the possible objects this can retrieve
        """
        return getJsonFileList(self.dirPath)

    def load(self, name: str):
        filePath = os.path.join(self.dirPath, formatFileName(name))
        obj = None
        with open(filePath) as file:
            obj = self.doLoad(json.loads(file.read()))
        return obj

    @abc.abstractmethod
    def doLoad(self, asJson: dict):
        pass
