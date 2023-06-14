from re        import Match, Pattern, fullmatch, compile, finditer
from functools import reduce
from operator  import iconcat

# a catagory holds characters together nealy, represented by a capital letter
class Catagory:
    def __init__(self, input_str: str) -> None:
        if fullmatch("[A-Z]=.+", input_str) == None:
            raise ValueError("must be in the form <Capital Letter>=<list of characters>")
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

# sound change object used both for detecting contexts where a sound change can occur, and applying sound changes
class SoundChange:
    def __init__(self, catagories: Catagory, input_val: str, output_val: str, context: str, nontexts: list[str], metathesize: bool) -> None:
        self.input_val  = input_val
        self.output_val = output_val
        self.context    = context
        self.nontexts   = nontexts
        self.metathesize= False

        self.context_undescore_positions = [
            index for index, character in enumerate(context) if character == "_"
        ]
        self.nontext_underscore_positions = [[
                index for index, character in enumerate(nontext) if character == "_"
            ] for nontext in nontexts
        ]

        self.context_pattern  = self.compile_context_pattern(context, catagories)
        self.nontext_patterns = [self.compile_context_pattern(nontext, catagories) for nontext in nontexts]

    # used to substitute the input into the context so that it can find matches
    def substitute_into_context(self, context: str, value: str) -> str:
         return context.replace("_", value) if "_" in context else context 

    # curlies are used for optionals which in regex is []?
    def substitute_brackets(self, context: str) -> str:
        return context.replace("(", "[").replace(")", "]?")

    # substitutes the catagory strings into the regex
    def substitute_catagories(self, context: str, catagories: Catagories) -> str:
        completed = ""
        for character in list(context):
            catagory = catagories[character]
            if catagory == None:
                completed += character
                continue
            completed += catagory
        return completed

    # ellipses are used for any number of character
    def substitute_ellipses(self, context: str) -> str:
        return context.replace("...", ".+")

    # embeded brackets may cause issues for regex, so inner brackets are removed
    def remove_higher_level_brackets(self, context: str) -> str:
        completed = ""
        current_level = 0
        for character in list(context):
            if character == "[": current_level += 1
            if character == "]": current_level -= 1
            if not(character in "[]" and current_level > 1):
                completed += character
        return completed

    # squares like SCA²
    def replace_squares(self, context: str) -> str:
        completed = ""
        for character in list(context):
            completed += "{2}" if character == "²" else character
        return completed

    # compiles the pattern so it can be reused
    def compile_context_pattern(self, context: str, catagories: Catagories) -> Pattern: 
        context = self.substitute_into_context(context, self.input_val) # _ -> input_val
        context = self.substitute_brackets(context)                     # (X) -> [X]?
        context = self.substitute_catagories(context, catagories)       # X -> [xyz]
        context = self.substitute_ellipses(context)                     # ... -> .+
        context = self.remove_higher_level_brackets(context)            # [#[xyz]] -> [#xyz]
        context = self.replace_squares(context)                         # x² -> x{2}

        return compile(context)

    # replaces all valid context matches with "_" which is then replaced with self.output
    def replace_underscore_by_indexes(self, string: str, indexes: list[int], length: int):
         nindexes  = reduce(iconcat, [[i for i in range(index + 1, index + length)] for index in indexes], [])
         newstring = ""
         for index, character in enumerate(list(string)):
             if index in indexes:
                 newstring += "_"
                 continue
             if index in nindexes:
                 continue
             else:
                 newstring += character
         return newstring
   
    # when input is blank, inserts "_" which is replaced by self.output
    def insert_underscore_by_indexes(self, string: str, indexes: list[int]) -> str:
        newstring = ""
        for index, character in enumerate(list(string)):
            if index in indexes:
                newstring += "_" + character
                continue
            newstring += character
        if len(string) in indexes:
            newstring += "_"
        return newstring

    # obtains the positions of contexts that match the pattern but not which also match any nontexts
    def get_valid_positions(self, word: str) -> list[int]:
        context_matches = [ # finds all of the contexts for the sound change
            context_match for context_match in finditer(self.context_pattern, f"#{word}#")
        ]
        
        context_positions = [[ # finds all of the positions that are related to contexts
            context_match.start() + underscore_position
            for underscore_position in self.context_undescore_positions]
            for context_match in context_matches
        ]
        context_positions = reduce(iconcat, context_positions, [])

        nontext_matches = [[ # finds all of the nontexts (exceptions to contexts) for the sound change
            (nontext_match, nontext_pattern)
            for nontext_match in finditer(nontext_pattern, f"#{word}#")]
            for nontext_pattern in self.nontext_patterns
        ]
        nontext_matches = reduce(iconcat, nontext_matches, [])

        nontext_positions = [] # finds all of the positions that are related to nontexts
        for nontext_match in nontext_matches:
            position = -1
            for index, nontext_pattern in enumerate(self.nontext_patterns):
                if nontext_match[1] == nontext_pattern:
                    position = index
                    break
            nontext_positions.append([
                nontext_match[0].start() + underscore_position
                for underscore_position in self.nontext_underscore_positions[position]
            ])
        nontext_positions = reduce(iconcat, nontext_positions, [])
        
        # filters out context positions that are also nontexts
        valid_positions = list(set(context_positions).difference(set(nontext_positions)))
        valid_positions = [position - 1 for position in valid_positions] 
        
        return valid_positions

    # applies the sound change
    def apply(self, word: str) -> str:
        valid_positions = self.get_valid_positions(word)

        if self.metathesize:
            raise NotImplementedError("metathesis not implemented") # metathesis code

        if len(self.input_val) == 0:
            word = self.insert_underscore_by_indexes(word, valid_positions)
        else:
            word = self.replace_underscore_by_indexes(word, valid_positions, len(self.input_val))

        return word.replace("_", self.output_val)

# holds and applies sound changes
class SoundChanges:
    pass

# rewrite rules for 
class RewriteRule:
    pass

# rewrite 
class RewriteRules:
    pass

# holds input words
class InputWords:
    pass

def main():
    c = Catagories("V=aiueo\nC=ptkbdghmnŋslr")
    r = SoundChange (
        c,
        input("expected input: "),
        input("expected output: "),
        input("sound change context: "),
        [input("sound change nontext: ")],
        False
    )
    ws = input("word(s)").split(" ")
    ms = [r.apply(w) for w in ws]

    for i in range(len(ws)):
        print(ws[i] + " " + str(ms[i]))

if __name__ == "__main__":
    main()
