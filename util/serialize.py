from abc import ABC, abstractmethod
import json
from stat_classes import Stat



# new code here
class JsonSerializer:
    """
    The JsonSerializer class handles the serialization of objects within the
    program as JSON objects. Another class or function should handle writing to
    a file, as not every individual JSON object must be written to a file.
    """

    def __init__(self, type: str, serializedAttributes: "List<str>", helpers = Dict()):
        self.type = type
        self.serializedAttributes = serializedAttributes.copy()
        self.helpers = helpers.copy()

    def toJsonDict(self, obj)->dict:
        rawDict = Dict()
        rawDict[type] = self.type
        value = None
        for attribute in self.serializedAttributes:
            value = obj[value]
            if value.__class__.__name__ in self.helpers.keys(): # not sure about this part
                rawDict[attribute] = self.helpers[value.__class__.__name__].toJsonDict
            else:
                rawDict[attribute] = value
        return rawDict # or do I need to use JSON here?




# old code down here
class AbstractJsonSerialable(ABC): # allows this to use the "abstractmethod" annotation
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
        #for attr in self.serializedAttributes:
        #    print(attr, self.__dict__[attr])
        return json.loads(json.dumps({attr: self.__dict__[attr] for attr in self.serializedAttributes}, cls=CustomJsonEncoder))

    """
    Converts this' data to a json file,
    then saves it to a file
    """
    def writeToFile(self, filePath: str):
        with open(filePath, "w") as file:
            file.write(json.dumps(self.toJsonDict()))

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
