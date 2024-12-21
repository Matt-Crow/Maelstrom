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
            this may change if I add app data folders instead of storing in the
            project folder
        """
        self.dirPath = os.path.abspath(os.path.join(*dirPath.split(".")))

    def getOptions(self)->list[str]:
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

    def save(self, obj: "AbstractJsonSerialable"):
        path = os.path.join(self.dirPath, formatFileName(obj.name))
        with open(path, "w") as file:
            file.write(json.dumps(obj.toJson()))

    @abc.abstractmethod
    def doLoad(self, asJson: dict):
        pass

def formatFileName(serializableName: str)->str:
    """
    Formats an AbstractJsonSerialable's name (or any string for that matter)
    into an appropriate file name
    """
    return serializableName.replace(" ", "_") + ".json"

def unFormatFileName(fileName: str)->str:
    """
    Undoes the formatting from formatFileName
    """
    return fileName.replace(".json", "").replace("_", " ")

def getJsonFileList(dirPath: str)->list[str]:
    """
    Returns a list of all filenames of JSON files
    in the given dir, with the unFormatFileName applied
    to each of them.
    """
    ret = []
    ext = []
    for (dirPath, dirNames, fileNames) in walk(dirPath):
        for fileName in fileNames:
            ext = os.path.splitext(fileName)
            if len(ext) >= 2 and ext[1] == ".json":
                ret.append(unFormatFileName(fileName))
    return ret
