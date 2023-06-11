from re import search, fullmatch, Match

class Catagory:
    def __init__(self, input_str: str) -> None:
        if fullmatch("[A-Z]=.+", input_str) == None:
            raise ValueError("must be in the form <Capital Letter>=<list of characters>")
        self.symbol = input_str[0]
        self.characters = input_str[2:]

    def get_character_catagory(self) -> str:
        return "[" + self.characters + "]"

    def __eq__(self, key: str) -> bool:
        return key == self.symbol \
            or key == self.characters \
            or key == self.symbol + "=" + self.characters \
            or key == "[" + self.characters + "]" \

    def compare_length(self, other: 'Catagory') -> bool:
        return len(self.characters) == len(other.characters)

class Catagories:
    def __init__(self, input_lines: str) -> None:
        lines = input_lines.splitlines()
        self.catagories = [Catagory(line) for line in lines]

    def __getitem__(self, catagory_key: str) -> str | None:
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

    def substitute_into_context(self, context: str, value: str) -> str:
         return context.replace("_", value) if "_" in context else context

    def substitute_catagories(self, context: str, catagories: Catagories) -> str:
        completed = ""
        for character in context:
            catagory = catagories[character]
            if catagory == None:
                completed += character
                continue
            completed += catagory
        return completed

class ReplacementSC(SoundChange):
    def __init__(self, input_val: str, output_val: str, context: str, nontexts: list[str] = []) -> None:
        super().__init__(context, nontexts)
        self.input_val  = input_val
        self.output_val = output_val

    def compare_word(self, word: str, catagories: Catagories) -> Match | None:
        context = super().substitute_into_context(self.context, self.input_val)
        context = super().substitute_catagories(context, catagories)
        context = context.replace("...", ".+")
        context = context.replace("(", "").replace(")", "?")
        return search(context, word)

class SoundChanges:
    pass

class InputWords:
    pass

def main():
    c = Catagories("V=aiueo")
    r = ReplacementSC("i", "j", "V_V")
    m = r.compare_word("kaiu", c)
    print(m)

if __name__ == "__main__":
    main()
