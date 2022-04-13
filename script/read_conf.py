"""
Just reads the config file and returns it as a dictionnary.

Args:
    path: Path of the config file.
"""

import json


class Conf:
    """
    Just reads the config file and returns it as a dictionnary.

    Args:
        path: Path of the config file.
    """

    def __init__(self, path):
        """
        Just reads the config file and returns it as a dictionnary.

        Args:
            path: Path of the config file.
        """

        self.path = path

    def load(self):
        """
        Sends the help message in the provided channel id.

        Args:
            None

        Returns:
            json_object: returns a dictionnary read fron the json config file.
        """

        with open(self.path, 'r', encoding='utf-8') as file:
            json_object = json.load(file)
        return json_object
