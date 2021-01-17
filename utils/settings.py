import json
import sys


class Settings(dict):
    def __init__(self, source):
        try:
            with open(source, "r") as readfile:
                super().__init__(**json.load(readfile))
        except IOError:
            super().__init__()

    async def save(self):
        with open("settings.json", 'w') as writefile:
            json.dump(self, writefile)


sys.modules[__name__] = Settings("settings.json")
