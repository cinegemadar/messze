import pathlib

import pytest

import messze.structure


@pytest.mark.parametrize(
    ("pattern", "foot"),
    [
        ("LSS", ["dactyl"]),
        ("SS", ["pyrrhic"]),
        ("LS", ["trochee"]),
        ("LLL", ["spondee", "L"]),
    ],
)
def test_feet_recognition(pattern, foot):
    test_file = pathlib.Path("assets/tests/feet.json")
    feet = messze.structure.Trie(test_file)
    assert feet.recognize(pattern) == foot
