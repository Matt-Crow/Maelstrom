"""
Since many of the objects created by the program must persist across gameplay
sessions, this module allows them to be serialized as JSON, then stored to a
file, from whence they can later be loaded.
"""

import abc
import json
import os.path
from os import walk

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

class AbstractJsonLoader(object):
    def __init__(self, dirPath: str):
        """
        dirPath is relative to the project root
        """
        self._folder = os.path.abspath(os.path.join(*dirPath.split(".")))

    def get_options(self)->list[str]:
        """
        returns a list of all the possible objects this can retrieve
        """
        ret = []
        ext = []
        for (_, _, fileNames) in walk(self._folder):
            for fileName in fileNames:
                ext = os.path.splitext(fileName)
                if len(ext) >= 2 and ext[1] == ".json":
                    ret.append(fileName.replace(".json", "").replace("_", " "))
        return ret

    def load(self, name: str):
        filePath = os.path.join(self._folder, _format_file_name(name))
        obj = None
        with open(filePath) as file:
            obj = self.doLoad(json.loads(file.read()))
        return obj

    def save(self, obj: AbstractJsonSerialable):
        path = os.path.join(self._folder, _format_file_name(obj.name))
        with open(path, "w") as file:
            file.write(json.dumps(obj.toJson()))

    @abc.abstractmethod
    def doLoad(self, asJson: dict):
        pass

def _format_file_name(serializableName: str) -> str:
    """
    Formats an AbstractJsonSerialable's name into an appropriate file name
    """
    return serializableName.replace(" ", "_") + ".json"
