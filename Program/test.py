from catagories import Catagory, Catagories
from sound_changes import SoundChange, notation_to_SC


# used to debug applying sound changes to words
class SCTest:
    def __init__(self, notation: str, test_words: str | list[str], output_words: str | list[str]) -> None:
        self.notation = notation
        self.test_words = [test_words] if type(
            test_words) == type(str) else test_words
        self.output_words = [output_words] if type(
            output_words) == type(str) else output_words

        if len(test_words) != len(output_words):
            raise ValueError(
                "test and output word lists must be the same length")

    def get_test_words_len(self):
        return len(self.test_words)

    def test(self, catagories: Catagories, test_index: int = 0) -> tuple[bool, int]:
        all_successful = True
        number_successful = 0

        SC = notation_to_SC(catagories, self.notation)

        heading_buffer = "#" * (77 - len(f"Testing {self.notation}"))
        print(f"\033[0;34m# Testing {self.notation} {heading_buffer}\033[0m")

        for index, (test_word, output_word) in enumerate(zip(self.test_words, self.output_words)):
            new_word = SC.apply_to(test_word)

            if new_word == output_word:
                print(
                    f"{index + test_index} \033[1;32mTest Successful\033[0m:\t{test_word}\t->\t{new_word}")
                number_successful += 1
                continue
            print(
                f"{index + test_index} \033[1;31mTest Unsuccessful\033[0m:\t{test_word}\t->\t{new_word}, expected {output_word}")
            all_successful = False

        foot_buffer = "#" * 80
        print(f"\033[0;34m{foot_buffer}\033[0m\n")

        return (all_successful, number_successful)


# allows multiple numbered sound change tests at once
def test_multipleSCs(SC_tests: list[SCTest], catagories: Catagories) -> None:
    number_words_successful = 0
    number_SCs_successful = 0

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
