import pathlib

import messze.structure


def test_feet_recognition():
    test_file = pathlib.Path("assets/tests/feet.json")
    feet = messze.structure.Trie(test_file)
    assert feet.recognize("LSS") == ["dactyl"]
    assert feet.recognize("SS") == ["pyrrhic"]
    assert feet.recognize("LS") == ["trochee"]
    assert feet.recognize("LLL") == ["spondee", "L"]
