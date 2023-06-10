from re import match, fullmatch

class Catagory:
    def __init__(self, input_str: str) -> None:
        if fullmatch("[A-Z]=.+", input_str) == None:
            raise ValueError("must be in the form <Capital Letter>=<list of characters>")
        self.symbol = input_str[0]
        self.characters = input_str[2:]

    def get_character_catagory(self) -> str:
        return "[" + self.characters + "]"

    def __eq__(self, key: str | 'Catagory') -> bool:
        return key == self.symbol \
            or key == self.characters \
            or key == self.symbol + "=" + self.characters \
            or key == "[" + self.characters + "]" \
            or (key.symbol == self.symbol and key.characters == self.characters)

    def compare_length(self, other: 'Catagory') -> bool:
        return len(self.characters) == len(other.characters)

class Catagories:
    def __init__(self, input_lines: str) -> None:
        lines = input_lines.splitlines()
        self.catagories = [Catagory(line) for line in lines]

    def __getitem__(self, catagory_key: str | Catagory) -> str | None:
        for catagory in self.catagories:
            if catagory == catagory_key:
                return catagory.get_character_catagory()
        return None

# 4 types of Sound Change:
#   1) Replacement
#   2) Insertion
#   3) Deletion
#   4) Metathesis

class SoundChange:
    def __init__(self, context: str, nontexts: list[str]) -> None:
        self.context = context
        self.nontexts = nontexts

class ReplacementSC(SoundChange):
    def __init__(self, input_val: str, output_val: str, context: str, nontexts: list[str]) -> None:
        super().__init__(context, nontexts)
        self.input_val = input_val
        self.output_val = output_val

    def compare_word(self, word: str) -> bool:
        pass


class SoundChanges:
    pass

class InputWords:
    pass
