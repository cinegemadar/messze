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


def test_structure_str():
    test_file = pathlib.Path("assets/tests/feet.json")
    feet = messze.structure.Trie(test_file)
    print(str(feet))
    assert (
        (str(feet))
        == """('')
  ('S')
    ('L' <- iamb)
    ('S' <- pyrrhic)
      ('L' <- anapest)
  ('L')
    ('S' <- trochee)
      ('S' <- dactyl)
    ('L' <- spondee)
"""
    )
