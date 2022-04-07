import json

class Conf:

    def __init__(self, path):
        self.path = path

    def load(self):
        with open(self.path, 'r') as file:
            object = json.load(file)
        return object
