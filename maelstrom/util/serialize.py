"""
Since many of the objects created by the program must persist across gameplay
sessions, this module allows them to be serialized as JSON, then stored to a
file, from whence they can later be loaded.
"""

import json

class AbstractJsonSerialable(object):
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

    def toJson(self)->dict:
        """
        returns this' attributes to serialize,
        as a json dictionary.
        """
        return json.loads(json.dumps({attr: self.__dict__[attr] for attr in self.serializedAttributes}, cls=MaelstromJsonEncoder))

class MaelstromJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        ret = None
        if isinstance(obj, AbstractJsonSerialable):
            ret = obj.toJson()
        else:
            ret = json.JSONEncoder.default(self, obj)
        return ret
