import typing as t

import json
import os

import messze.structure as structure


def sanitize(
    text: list[str], sanitizer: t.Optional[t.Callable[[str], str]]
) -> list[str]:
    """Sanitizes the given text using the sanitizer function, or default if not given."""

    def _default_sanitizer(line: str) -> str:
        """Removes all non-alphanumeric characters from the given line."""
        return "".join(c for c in line if c.isalnum() or c.isspace()).lower()

    if sanitizer is None:  # Default sanitizer
        sanitizer = _default_sanitizer

    return list(map(sanitizer, text))


class Parser:
    def __init__(self):
        self._poem: structure.Poem
        self._corpus: t.List[str]
        self.title = ""

    def parse(
        self, path: t.Union[str, os.PathLike[str]], has_title: bool = True
    ) -> None:
        with open(path, encoding="utf-8") as in_file:
            corpus = in_file.readlines()  # lines
            self._corpus = corpus
            corpus = sanitize(corpus, sanitizer=None)  # sanitized lines
            if has_title:
                corpus = self.drop_title(corpus)  # without title
            self._poem = structure.Poem([structure.Line(line) for line in corpus])

    @property
    def corpus(self) -> t.List[str]:
        return self._corpus

    @property
    def poem(self) -> structure.Poem:
        return self._poem

    @property
    def to_json(self) -> str:
        json_repr = {"title": f"{self.title}", "Poem": self.poem.serialize()}
        return json.dumps(json_repr, indent=4, ensure_ascii=False)

    def drop_title(self, lines: list[str]) -> list[str]:
        """Drops all lines before the second non-empty line."""
        non_empty_count = 0
        for index, line in enumerate(lines):
            if line.strip():
                non_empty_count += 1
                if non_empty_count == 2:
                    self.title = lines[index - 1].strip()
                    return lines[index:]
                else:
                    self.title = line.strip()
        return []  # Return an empty list if there are less than two non-empty lines

    def __repr__(self):
        return "\n".join(map(repr, self.corpus))

    def __str__(self):
        return "\n".join(map(str, self.corpus))
