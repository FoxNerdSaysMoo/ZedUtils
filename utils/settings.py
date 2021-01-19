import json
import sys


class Data(dict):
    def __init__(self, source):
        self.source = source
        try:
            with open(source, "r") as readfile:
                super().__init__(**json.load(readfile))
        except IOError:
            super().__init__()

    def save(self):
        with open(self.source, 'w') as writefile:
            json.dump(self, writefile, indent=4)


sys.modules[__name__] = Data
