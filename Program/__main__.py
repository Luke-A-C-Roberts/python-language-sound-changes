from catagories import Catagories
from test import test_multipleSCs, SCTest

# holds input words
class InputWords:
    pass

def main():
    catagories = Catagories("V=aiueo\nC=ptkbdghmnŋslr\nX=ptk\nY=bdg")

    test_multipleSCs([
        SCTest(
            "i/j/[V#]_V/_o",
            ["kaia", "iam", "kaio", "iom"],
            ["kaja", "jam", "kaio", "iom"]
        ),
        SCTest(
            "mb/mm/V_V",
            ["amba", "amb", "mba", "mb", "ambamba"],
            ["amma", "amb", "mba", "mb", "ammamma"],
        ),
        SCTest(
            "/j/kt_",
            ["akto", "akt", "aktakto"],
            ["aktjo", "aktj", "aktjaktjo"]
        ),
        SCTest(
            "/j/_kt",
            ["akto", "kto", "aktakto"],
            ["ajkto", "jkto", "ajktajkto"]
        ),
        SCTest(
            "/j/k_t",
            ["akto", "aktakto"],
            ["akjto", "akjtakjto"]
        ),
        SCTest(
            "a/o/ah_",
            ["naha"],
            ["naho"]
        ),
        SCTest(
            "V²/a/_",
            ["kaam"],
            ["kam"]
        ),
        SCTest(
            "X/Y/V_V",
            ["apa","apake"],
            ["aba","abage"]
        )
    ], catagories)


if __name__ == "__main__":
    main()
