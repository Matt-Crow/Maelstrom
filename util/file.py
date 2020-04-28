import os
from utilities import *

"""
This will replace all of
the aweful JSON and XML
stuff the project currently
uses.
"""
def writeCsvFile(filePath, headers, lineSupplier):
    with open(filePath, "w") as file:
        file.write(", ".join((header.lower() for header in headers)))
        for line in lineSupplier:
            file.write("\n" + line.strip())

def readCsvFile(filePath, requiredHeaders, lineConsumer):
    with open(filePath, "r") as file:
        for line in file:
            print(line)

if __name__ == "__main__":
    writeCsvFile("C:\\Users\\Matt\\Desktop\\test.csv", ["a", "b", "c"], ["1,2,3", "4,5,6"])


# Oof. Redo all of this... stuff.
class File(object):
    description_key = "<desc>"
    prescript_key = "<pre>"
    postscript_key = "<post>"
    script_key = "<script>"
    def __init__(self, file_name):
        self.file = file_name
        self.error = False
        self.load()

    def load(self):
        self.raw_data = []
        try:
            file = open(self.file, 'r')
            for line in file:
                self.raw_data.append(line.strip())
            file.close()
        except:
            self.error = True

    def get_lines(self):
        """
        Gets the raw data from this file
        """
        return self.raw_data.copy()

    def create_dict(self, split):
        """
        Create a dictionary,
        where everything prior
        to split is the key,
        after is the data
        """
        self.dictionary = dict()
        current_key = None

        for line in self.raw_data:
            omit = False

            # ignore blank lines
            if not line in ('\n', '\r\n'):
                # Go through the letters in the line...
                for i in range(0, len(line)):
                    # a split symbolizes a change in key for our dictionary
                    if line[i] == split:
                        # grab everything prior to the split
                        current_key = line[0:i]
                        # create a list for that key
                        self.dictionary[current_key] = list()
                        # don't append the key to its list
                        omit = True

                if not omit:
                    self.dictionary[current_key].append(line)

    def grab_key(self, key):
        ret = ("ERROR", "Key " + key, "does not exist for file", self.file)
        if key in self.dictionary.keys():
            ret = self.dictionary[key]
        return ret

    def save(self):
        file = open(self.file, 'w')
        for line in self.raw_data:
            write = line
            if not contains(line, "\n"):
                write += "\n"
            file.write(write)

class PlayerSaveFile(File):
    def save_data_from(self, player):
        self.raw_data = player.generate_save_code()
        self.save()
