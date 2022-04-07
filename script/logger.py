from datetime import datetime
import sys

class Logger:

    def __init__(self, level):
        self.LOG_LEVELS = { 'NONE'      : 6,
                            'SPECIAL'   : 6,
                            'TRACE'     : 5,
                            'DEBUG'     : 4,
                            'INFO'      : 3,
                            'CRITICAL'  : 2,
                            'WARNING'   : 1,
                            'ERROR'     : 1}
        self.LEVEL_INT = self.LOG_LEVELS[level.upper()]
        self.LEVEL_STR = level.upper()

    def log(self, level, message):
        if level.upper() == "NONE" :
            sys.stdout.write(f"#### {message}. ####\n")

        elif level.upper() == "SPECIAL":
            sys.stdout.write(message)

        elif level.upper() not in self.LOG_LEVELS.keys():
            sys.stderr.write(f"{level.upper()} is not a valid log level.\n")

        else:
            if self.LOG_LEVELS[level.upper()] <= self.LEVEL_INT:
                time_to_print = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                to_send = f"[{level.upper()}] [{time_to_print}] : {message}.\n"

                if self.LOG_LEVELS[level.upper()] <= 2:
                    sys.stderr.write(to_send)
                else:
                    sys.stdout.write(to_send)

    def change_log_level(self, level):
        self.LEVEL_INT = self.LOG_LEVELS[level.upper()]
        self.LEVEL_STR = level.upper()

    def get_log_level():
        return (self.LEVEL_INT, self.LEVEL_STR)

    def get_log_level_int():
        return self.LEVEL_INT

    def get_log_level_str():
        return self.LEVEL_STR
