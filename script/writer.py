import json

class Writer:

    def __init__(self, path):
        self.path = path

    def write(self, json_object):
        with open(self.path, 'w') as file:
            json.dump(json_object, file)

    def load(self):
        with open(self.path, 'r') as file:
            object = json.load(file)
        return object
