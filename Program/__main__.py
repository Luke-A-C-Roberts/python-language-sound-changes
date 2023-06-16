from re        import Match, Pattern, fullmatch, compile, finditer
from functools import reduce
from operator  import iconcat
from itertools import filterfalse

# a catagory holds characters together nealy, represented by a capital letter
class Catagory:
    def __init__(self, input_str: str) -> None:
        if fullmatch("[A-Z]=.+", input_str) == None:
            raise ValueError("must be in the form <capital letter>=<list of characters>")
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

        self.input_pattern = self.compile_context_pattern(input_val, catagories)

        self.context_pattern = self.compile_context_pattern(
            self.substitute_into_context(context, input_val), catagories
        )
        
        self.nontext_patterns = [
            self.compile_context_pattern(self.substitute_into_context(nontext, input_val), catagories)
            for nontext in nontexts
        ]

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
            if not(character in "[]" and current_level > 1):
                completed += character
            if character == "]": current_level -= 1
        return completed

    # squares like SCA²
    def replace_squares(self, context: str) -> str:
        completed = ""
        for character in list(context):
            completed += "{2}" if character == "²" else character
        return completed

    # compiles the pattern so it can be reused
    def compile_context_pattern(self, context: str, catagories: Catagories) -> Pattern: 
        context = self.substitute_brackets(context)                     # (X) -> [X]?
        context = self.substitute_catagories(context, catagories)       # X -> [xyz]
        context = self.substitute_ellipses(context)                     # ... -> .+
        context = self.remove_higher_level_brackets(context)            # [#[xyz]] -> [#xyz]
        context = self.replace_squares(context)                         # x² -> x{2}
        print(context)
        return compile(context)

    # used to find if an input match is inside of a context match. used to select which contexts to SC
    def is_in_context(self, input_match: Match, context_match: Match) -> bool:
        return context_match.start() <= input_match.start() and input_match.end() <= context_match.end()

    def generate_output(self, input_match_string: str) -> str:
        if self.metathesize:
            raise NotImplementedError("metathesis is not implemented")
        return self.output_val

    # obtains the positions of contexts that match the pattern but not which also match any nontexts
    def obtain_input_matches(self, word: str) -> list[Match]:

        input_matches = [ # finds all of the inputs presesnt in the word
            input_match for input_match in finditer(self.input_pattern, word)
        ]

        context_matches = [ # finds all of the contexts for the sound change
            context_match for context_match in finditer(self.context_pattern, word)
        ]

        nontext_matches = [[ # finds all of the nontexts (exceptions to contexts) for the sound change
            nontext_match for nontext_match in finditer(nontext_pattern, word)]
            for nontext_pattern in self.nontext_patterns
        ]
        nontext_matches = reduce(iconcat, nontext_matches, [])

        is_in_context_lmd = lambda input_match: any( # lambda for filtering which input matches are inside context matches
            self.is_in_context(input_match, context_match) for context_match in context_matches
        )
        input_matches = [context for context in filter(is_in_context_lmd, input_matches)] # filter those that match

        is_in_nontext_lmd = lambda input_match: any( # similar lamda for nontexts
            self.is_in_context(input_match, nontext_match) for nontext_match in nontext_matches
        )
        input_matches = [context for context in filterfalse(is_in_nontext_lmd, input_matches)] # filter those that do not match

        print(input_matches)
        
        return input_matches

    def apply_to(self, word: str) -> str:
        word = f"#{word}#"

        input_matches = self.obtain_input_matches(word)

        if input_matches == []:
            return word[1:-1]

        match_positions = [[i for i in range(this_match.start(), this_match.end())] for this_match in input_matches]
        match_positions = set(reduce(iconcat, match_positions, []))
        literal_positions = list(set(range(len(word))).difference(match_positions))
        substitute_positions = [this_match.start() for this_match in input_matches]

        new_word = ""
        for position, character in enumerate(word):
            if position in literal_positions:
                new_word += character
                continue
            if not position in substitute_positions:
                continue
            this_match = [input_match for input_match in input_matches if input_match.start() == position][0]
            new_word += self.generate_output(this_match.group(0))

        return new_word[1:-1]

def notation_to_SC(catagories: Catagories, notation: str) -> SoundChange:
   sections = notation.split("/")
   if len(sections) < 3:
       raise ValueError("notation must be in the form <input>/<output>/<context>[/<nontexts>]")
   
   if len(sections) == 3:
       return SoundChange(catagories, sections[0], sections[1], sections[2], [], False)

   return SoundChange(catagories, sections[0], sections[1], sections[2], sections[3:], False)

def test_sound_change(notation: str, catagories: Catagories, test_words: str | list[str], output_words: str | list[str]) -> None:
    SC = notation_to_SC(catagories, notation)

    if type(test_words) == type(str):
        test_words = [test_words]

    if type(output_words) == type(str):
        output_words = [output_words]

    if len(test_words) != len(output_words):
        raise ValueError("test and output word lists must be the same length")

    for index, (test_word, output_word) in enumerate(zip(test_words, output_words)):
        new_word = SC.apply_to(test_word)
        
        if new_word == output_word:
            print(f"{index} \033[1;32mTest Successful\033[0m: {test_word} -> {notation} -> {new_word}")
            continue
        
        print(f"{index} \033[1;31mTest Unsuccessful\033[0m: {test_word} -> {notation} -> {new_word}, expected {output_word}")

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
    catagories = Catagories("V=aiueo\nC=ptkbdghmnŋslr")
    
    test_sound_change(
        "i/j/[V#]_V/_o",
        catagories,
        ["kaia", "iam", "kaio", "iom"],
        ["kaja", "jam", "kaio", "iom"]
    )

if __name__ == "__main__":
    main()
