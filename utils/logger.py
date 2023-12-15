from datetime import datetime
from termcolor import colored


class Logger:
    def __init__(self, name: str):
        self.name = name

    def info(self, msg: str):
        current_dateTime = datetime.now()
        print(f"{current_dateTime} INFO {self.name}: {msg}")

    def debug(self, msg: str):
        current_dateTime = datetime.now()
        print(f"{current_dateTime} DEBUG {self.name}: {msg}")

    def error(self, msg: str):
        current_dateTime = datetime.now()
        print(colored(f"{current_dateTime} INFO {self.name}: {msg}", "red"))
