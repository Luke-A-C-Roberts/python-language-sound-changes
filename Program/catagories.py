from re import fullmatch

# a catagory holds characters together nealy, represented by a capital letter
class Catagory:
    def __init__(self, input_str: str) -> None:
        if fullmatch("[A-Z]=.+", input_str) == None:
            raise ValueError(
                "must be in the form <capital letter>=<list of characters>")
        self.symbol = input_str[0]
        self.characters = input_str[2:]

    def get_character_catagory(self) -> str:
        return "[" + self.characters + "]"

    # multiple ways for a Catagory to be equal
    def __eq__(self, key: str) -> bool:
        return key == self.symbol \
            or key == self.characters \
            or key == self.symbol + "=" + self.characters \
            or key == "[" + self.characters + "]" \

    # used for special cases where a catagory is both the input and output of a sound change
    def compare_length(self, other: 'Catagory') -> bool:
        return len(self.characters) == len(other.characters)

# holds catagories neatly together
class Catagories:
    def __init__(self, input_lines: str) -> None:
        lines = input_lines.splitlines()
        self.catagories = [Catagory(line) for line in lines]

    # a single catagory can be retrieved based on the key capital letter inputted
    def __getitem__(self, catagory_key: str) -> str | None:
        for catagory in self.catagories:
            if catagory == catagory_key:
                return catagory.get_character_catagory()
        return None
