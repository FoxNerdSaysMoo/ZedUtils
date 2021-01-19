class Inventory:
    def __init__(self, contents: list, suffixes: dict = {}):
        self.contents = dict(contents)
        self.suffixes = suffixes

    def __add__(self, other):
        if str(other) not in self.contents.keys():
            self.contents[str(other)] = 1
        else:
            self.contents[str(other)] += 1
    
    def __sub__(self, other):
        self.contents[str(other)] -= 1

    def __str__(self):
        return '\n'.join(
            [f'{y}x {x + self.suffixes[x] if x in self.suffixes else x}' for x, y in self.contents.items() if y > 0]
        )

    def __contains__(self, item):
        if isinstance(item, str):
            return self.contents.keys().__contains__(item)
        else:
            pair = tuple(item)
            if pair[0] in self.contents.keys():
                if pair[1] <= self.contents[pair[0]]:
                    return True
            return False
    
    def len(self):
        length = 0
        for x, y in self.contents.items():
           length += y
        return length

