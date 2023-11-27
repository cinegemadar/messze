import messze.parser


def test_sanitize():
    phrase = ("27", "28", "...", "@", "almafa", "korte")
    assert messze.parser.sanitize(text=list(phrase), sanitizer=None) == [
        "27",
        "28",
        "",
        "",
        "almafa",
        "korte",
    ]
    assert messze.parser.sanitize(text=list(phrase), sanitizer=lambda x: x) == [
        "27",
        "28",
        "...",
        "@",
        "almafa",
        "korte",
    ]


def test_drop_title():
    parser = messze.parser.Parser()
    assert parser.drop_title(lines=[]) == []
    assert parser.title == ""
    assert parser.drop_title(lines=["   TITLE   ", "NOT TITLE"]) == ["NOT TITLE"]
    assert parser.title == "TITLE"


def test_parse():
    parser = messze.parser.Parser()
    parser.parse(path="assets/tests/petofi.txt", has_title=False)
    assert parser.title == ""
    assert parser.corpus[0][:9] == "Szeretnek"
