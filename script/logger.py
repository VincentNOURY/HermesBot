"""
Logger is a class that format logs.

Args:
    level: The level of logs
"""

from datetime import datetime
import sys


class Logger:
    """
    Logger is a class that formats logs.

    Args:
        level: The level of logs
    """

    def __init__(self, level):
        """
        Sends the help message in the provided channel id.

        Args:
            level: The level of logs

        Returns:
            None
        """

        self.log_levels = {'NONE':       6,
                           'SPECIAL':    6,
                           'TRACE':      5,
                           'DEBUG':      4,
                           'INFO':       3,
                           'CRITICAL':   2,
                           'WARNING':    1,
                           'ERROR':      1}

        self.level_int = self.log_levels[level.upper()]
        self.level_str = level.upper()

    def log(self, level, message):
        """
        Logs the message if level is equal or lower to the level indicated.

        Args:
            channel_id: Id of the channel the help message is ment to be sent.

        Returns:
            None
        """

        if level.upper() == "NONE":
            sys.stdout.write(f"#### {message}. ####\n")

        elif level.upper() == "SPECIAL":
            sys.stdout.write(message)

        elif level.upper() not in self.log_levels.keys():
            sys.stderr.write(f"{level.upper()} is not a valid log level.\n")

        else:
            if self.log_levels[level.upper()] <= self.level_int:
                time_to_print = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                to_send = f"[{level.upper()}] [{time_to_print}] : {message}.\n"

                if self.log_levels[level.upper()] <= 2:
                    sys.stderr.write(to_send)
                else:
                    sys.stdout.write(to_send)

    def change_log_level(self, level):
        """
        Changes the log level.

        Args:
            level: New level of logs.

        Returns:
            None
        """

        self.level_int = self.log_levels[level.upper()]
        self.level_str = level.upper()

    def get_log_level(self):
        """
        Get the log level as a tuple (int, str).

        Args:
            None

        Returns:
            The log level as a tuple (level: integer, level: str).
        """

        return (self.level_int, self.level_str)

    def get_log_level_int(self):
        """
        Get the log level as an int.

        Args:
            channel_id: Id of the channel the help message is ment to be sent.

        Returns:
            None
        """

        return self.level_int

    def get_log_level_str(self):
        """
        Get the log level as a string.

        Args:
            None

        Returns:
            The log level as a string.
        """

        return self.level_str
