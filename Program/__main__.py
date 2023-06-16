from re        import Match, Pattern, fullmatch, compile, finditer, search
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

        self.input_pattern = self.__compile_context_pattern(input_val, catagories)

        self.context_pattern = self.__compile_context_pattern(
            self.__substitute_into_context(context, input_val), catagories
        )
        
        self.nontext_patterns = [
            self.__compile_context_pattern(self.__substitute_into_context(nontext, input_val), catagories)
            for nontext in nontexts
        ]

        print(context.split("_"))
        self.context_bodies = [
            self.__compile_context_pattern(context_body, catagories)
            for context_body in context.split("_")
        ]

    # used to substitute the input into the context so that it can find matches
    def __substitute_into_context(self, context: str, value: str) -> str:
         return context.replace("_", value) if "_" in context else context 

    # curlies are used for optionals which in regex is []?
    def __substitute_brackets(self, context: str) -> str:
        return context.replace("(", "[").replace(")", "]?")

    # substitutes the catagory strings into the regex
    def __substitute_catagories(self, context: str, catagories: Catagories) -> str:
        completed = ""
        for character in list(context):
            catagory = catagories[character]
            if catagory == None:
                completed += character
                continue
            completed += catagory
        return completed

    # ellipses are used for any number of character
    def __substitute_ellipses(self, context: str) -> str:
        return context.replace("...", ".+")

    # embeded brackets may cause issues for regex, so inner brackets are removed
    def __remove_higher_level_brackets(self, context: str) -> str:
        completed = ""
        current_level = 0
        for character in list(context): 
            if character == "[": current_level += 1
            if not(character in "[]" and current_level > 1):
                completed += character
            if character == "]": current_level -= 1
        return completed

    # squares like SCA²
    def __replace_squares(self, context: str) -> str:
        completed = ""
        for character in list(context):
            completed += "{2}" if character == "²" else character
        return completed

    # compiles the pattern so it can be reused
    def __compile_context_pattern(self, context: str, catagories: Catagories) -> Pattern: 
        context = self.__substitute_brackets(context)                     # (X) -> [X]?
        context = self.__substitute_catagories(context, catagories)       # X -> [xyz]
        context = self.__substitute_ellipses(context)                     # ... -> .+
        context = self.__remove_higher_level_brackets(context)            # [#[xyz]] -> [#xyz]
        context = self.__replace_squares(context)                         # x² -> x{2}
        return compile(context)

    def __generate_output(self, input_match_string: str) -> str:
        if self.metathesize:
            raise NotImplementedError("metathesis is not implemented")
        return self.output_val

    # finds all of the inputs presesnt in the word
    def __obtain_input_matches(self, word: str) -> list[Match]:
        return [input_match for input_match in finditer(self.input_pattern, word)]

    # finds all of the contexts for the sound change
    def __obtain_context_matches(self, word: str) -> list[Match]:
        return [context_match for context_match in finditer(self.context_pattern, word)]

    # finds all of the nontexts (exceptions to contexts) for the sound change
    def __obtain_nontext_matches(self, word: str) -> list[Match]:
        nontext_matches = [[
            nontext_match for nontext_match in finditer(nontext_pattern, word)]
            for nontext_pattern in self.nontext_patterns
        ]
        return reduce(iconcat, nontext_matches, [])

    # used to find if an input match is inside of a context match. used to select which contexts to SC
    def __is_in_context(self, input_match: Match, context_match: Match) -> bool:
        return context_match.start() <= input_match.start() and input_match.end() <= context_match.end()

    def __is_in_sub_context(self, input_match: Match, sub_context_span: tuple[int]) -> bool:
        return sub_context_span[0] <= input_match.start() and input_match.end() <= sub_context_span[1]
    
    # obtains the positions of contexts that match the pattern but not which also match any nontexts
    def __obtain_valid_matches(self, word: str) -> list[Match]:

        input_matches   = self.__obtain_input_matches(word)
        context_matches = self.__obtain_context_matches(word)
        nontext_matches = self.__obtain_nontext_matches(word)
        
        # lambda for filtering which input matches are inside context matches
        is_in_context_lmd = lambda input_match: any(
            self.__is_in_context(input_match, context_match) for context_match in context_matches
        )
        # similar lamda for nontexts
        is_in_nontext_lmd = lambda input_match: any(
            self.__is_in_context(input_match, nontext_match) for nontext_match in nontext_matches
        )

        input_matches = [context for context in filter(is_in_context_lmd, input_matches)] # filter those that match a context
        input_matches = [context for context in filterfalse(is_in_nontext_lmd, input_matches)] # filter thoes that are not in a nontext

        # filter out input matches that are also in a context body

        all_sub_context_spans = []
        for context_match in context_matches:
            context_str = context_match.group(0)
            start_pos = context_match.start()

            sub_context_spans: list[tuple[int]] = []

            for context_body_pattern in self.context_bodies:
                print(f"'{context_body_pattern.pattern}'")

                context_body_match = search(context_body_pattern, context_str)

                if not context_body_match: break
                context_str = context_str[:context_body_match.end()]

                sub_context_spans.append((start_pos, start_pos + context_body_match.end()))
                start_pos += context_body_match.end()

                if self.input_pattern == "": continue

                input_match = search(self.input_pattern, context_str)
                if not input_match: break
                context_str = context_str[:input_match.end()]

            all_sub_context_spans.append(sub_context_spans)

        all_sub_context_spans = [
            span for span in
            filterfalse(lambda span: span[0] == span[1], reduce(iconcat, all_sub_context_spans, []))
        ]

        print("input matches:", [input_match.span() for input_match in input_matches])
        print("sub context span:", all_sub_context_spans)

        # lambda for seeing which input are inside a sub context
        is_in_sub_context_lmd = lambda input_match: any(
            self.__is_in_sub_context(input_match, sub_context_span)
            for sub_context_span in all_sub_context_spans
        )
        # filters inputs which are not in sub contexts
        input_matches = [context for context in filterfalse(is_in_sub_context_lmd, input_matches)]

        print("filtered input matches:", [input_match.span() for input_match in input_matches])

        return input_matches

    def apply_to(self, word: str) -> str:

        # add word endings and get the input matches
        word = f"#{word}#"
        valid_matches = self.__obtain_valid_matches(word)

        match_positions = [[i for i in range(this_match.start(), this_match.end())] for this_match in valid_matches]
        match_positions = set(reduce(iconcat, match_positions, []))
        literal_positions = list(set(range(len(word))).difference(match_positions))
        substitute_positions = [this_match.start() for this_match in valid_matches]

        new_word = ""
        for position, character in enumerate(word):
            if position in literal_positions:
                new_word += character
                continue

            if not position in substitute_positions:
                continue

            this_match = [valid_match for valid_match in valid_matches if valid_match.start() == position][0]
            new_word += self.__generate_output(this_match.group(0))

        return new_word[1:-1]

def notation_to_SC(catagories: Catagories, notation: str) -> SoundChange:
   sections = notation.split("/")
   if len(sections) < 3:
       raise ValueError("notation must be in the form <input>/<output>/<context>[/<nontexts>]")
   
   if len(sections) == 3:
       return SoundChange(catagories, sections[0], sections[1], sections[2], [], False)

   return SoundChange(catagories, sections[0], sections[1], sections[2], sections[3:], False)

class SCTest:
    def __init__(self, notation: str, test_words: str | list[str], output_words: str | list[str]) -> None:
        self.notation    = notation
        self.test_words  = [test_words]   if type(test_words)   == type(str) else test_words
        self.output_words= [output_words] if type(output_words) == type(str) else output_words

        if len(test_words) != len(output_words):
            raise ValueError("test and output word lists must be the same length")

    def get_test_words_len(self):
        return len(self.test_words)

    def test(self, catagories: Catagories, test_index: int = 0) -> tuple[bool, int]:
        all_successful    = True
        number_successful = 0

        SC = notation_to_SC(catagories, self.notation)

        heading_buffer = "#" * (77 - len(f"Testing {self.notation}"))
        print(f"\033[0;34m# Testing {self.notation} {heading_buffer}\033[0m")

        for index, (test_word, output_word) in enumerate(zip(self.test_words, self.output_words)):
            new_word = SC.apply_to(test_word)
        
            if new_word == output_word:
                print(f"{index + test_index} \033[1;32mTest Successful\033[0m:\t{test_word}\t->\t{new_word}")
                number_successful += 1
                continue
            print(f"{index + test_index} \033[1;31mTest Unsuccessful\033[0m:\t{test_word}\t->\t{new_word}, expected {output_word}")
            all_successful = False

        foot_buffer = "#" * 80
        print(f"\033[0;34m{foot_buffer}\033[0m\n")

        return (all_successful, number_successful)

def test_multipleSCs(SC_tests: list[SCTest], catagories: Catagories) -> None:
    number_words_successful = 0
    number_SCs_successful   = 0

    SC_count = len(SC_tests)
    word_count = sum([SC_test.get_test_words_len() for SC_test in SC_tests])

    SC_test_number = 0
    for SC_test in SC_tests:
        test_results = SC_test.test(catagories, SC_test_number)
        SC_test_number += SC_test.get_test_words_len()
        number_SCs_successful += 1 if test_results[0] else 0
        number_words_successful += test_results[1]
    
    print(f"{number_words_successful} / {word_count} words successful.")
    print(f"{number_SCs_successful} / {SC_count} SCs successful.")

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
    
    test_multipleSCs([
        SCTest(
            "/j/kt_/_#",
            ["akto", "akt"],
            ["aktjo", "akt"]
        ),
        SCTest(
            "/j/_kt",
            ["akto"],
            ["ajkto"]
        ),
        SCTest(
            "/j/k_t",
            ["akto"],
            ["akjto"]
        ),
    ], catagories)

    #test_sound_change ()

if __name__ == "__main__":
    main()
