from catagories import Catagories
from test import test_multipleSCs, SCTest

# holds input words
class InputWords:
    pass

def main():
    catagories = Catagories("V=aiueo\nC=ptkbdghmnŋslr")

    test_multipleSCs([
        SCTest(
            "i/j/[V#]_V/_o",
            ["kaia", "iam", "kaio", "iom"],
            ["kaja", "jam", "kaio", "iom"]
        ),
        SCTest(
            "mb/mm/V_V",
            ["amba", "amb", "mba", "mb"],
            ["amma", "amb", "mba", "mb"],
        ),
        SCTest(
            "/j/kt_",
            ["akto", "akt"],
            ["aktjo", "aktj"]
        ),
        SCTest(
            "/j/_kt",
            ["akto", "kto"],
            ["ajkto", "jkto"]
        ),
        SCTest(
            "/j/k_t",
            ["akto"],
            ["akjto"]
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
        )
    ], catagories)


if __name__ == "__main__":
    main()
