class File(object):
    def __init__(self, file_name):
        self.file = file_name
        self.load()
    
    def load(self):
        self.raw_data = []
        file = open(self.file, 'r')
        for line in file:
            self.raw_data.append(line)
        file.close()
    
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
            file.write(line)