"""
This file provides the utilities that handle the conversion of JSON files to
objects within the program. In this way, the process of creating objects is
decoupled from the objects themselves.

Will need to split into file loaders and JSON decoders, as those fulfill
different tasks
"""


import os.path
import json
import abc
from fileSystem import formatFileName, unFormatFileName, getJsonFileList



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
