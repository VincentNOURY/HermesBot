"""
Writer is a class only used for reading and writing to a json file
"""

import json


class Writer:
    """
    Writer class is used for reading and writing to a json file

    Args:
        path: Path of the file to write to / read from
    """

    def __init__(self, path):
        """
        Initialization of the writer class

        Args:
            path: Path of the file to write to / read from.

        Returns:
            None
        """

        self.path = path

    def write(self, json_object):
        """
        Writes to a json file.

        Args:
            json_object: Dictionnary used to be dumped into the file.

        Returns:
            None
        """

        with open(self.path, 'w', encoding='utf-8') as file:
            json.dump(json_object, file)

    def load(self):
        """
        Loads the json / dictionnary object from a file.

        Args:
            None

        Returns:
            json_object: Dictionnary loaded from the json file.
        """

        with open(self.path, 'r', encoding='utf-8') as file:
            json_object = json.load(file)
        return json_object
