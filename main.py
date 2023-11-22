import pathlib

import icecream as ic

from messze import parser as parser
from messze import structure as structure


def main():
    p = parser.Parser()
    # p.parse(pathlib.Path("assets/tests/babits.txt"))
    p.parse(pathlib.Path("assets/tests/petofi.txt"), has_title=False)
    # p.parse(pathlib.Path("assets/tests/ja.txt"))
    vers = p.poem
    feet = structure.Trie("assets/tests/feet.json")
    for line in vers:
        if line.get_repr == "":
            continue
        ic.ic(str(line))
        ic.ic(line.get_repr)
        ic.ic(feet.recognize(line.get_repr))


if __name__ == "__main__":
    main()
