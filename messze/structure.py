import typing as t

import dataclasses
import json
import re


class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word: bool = False
        self.name: str = ""


class Trie:
    def __init__(self, json_file_path=None):
        self.root = TrieNode()
        if json_file_path:
            self._build_trie_from_json(json_file_path)

    def _build_trie_from_json(self, json_file_path):
        with open(json_file_path) as json_file:
            data = json.load(json_file)
            for foot in data["legs"]:
                self.insert(foot["pattern"], foot["name"])

    def insert(self, word, name):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        node.name = name

    def fit(self, string: str, is_short: bool) -> t.List[str]:
        current_node = self.root
        for index, char in enumerate(string):
            remaining_string = string[index:]
            if char in current_node.children:
                current_node = current_node.children[char]
                if current_node.is_end_of_word and is_short:
                    return [current_node.name] + self.fit(remaining_string, is_short)
                continue
            if current_node.is_end_of_word:
                return [current_node.name] + self.fit(remaining_string, is_short)
            else:
                raise ValueError(f"Pattern {string} not found")
        return [current_node.name] if current_node.is_end_of_word else [string]

    def recognize(self, string: str) -> t.List[str]:
        long = self.fit(string, is_short=False)
        short = self.fit(string, is_short=True)
        no_of_incomplete = lambda x: sum(1 for foot in x if foot == "None")
        return short if no_of_incomplete(short) < no_of_incomplete(long) else long

    def __str__(self):
        return self._node_to_string(self.root, "", "")

    def _node_to_string(self, node, char, prefix):
        if node is None:
            return ""
        node_repr = (
            f"{prefix}('{char}'"
            + (f" <- {node.name}" if node.is_end_of_word else "")
            + ")\n"
        )
        if node.children:
            for child_char, child_node in node.children.items():
                child_repr = self._node_to_string(child_node, child_char, prefix + "  ")
                node_repr += child_repr
        return node_repr


# # Example usage
# if __name__ == "__main__":
#     # Assuming 'legs.json' contains the metrical feet patterns
#     trie = Trie("legs.json")
#     print(trie)


def strip_if(text: str) -> str:
    """Strips the given text if it is not empty. Keeps 1 space on each side."""
    origin = text
    right, left = "", ""
    if not text.strip():
        return ""
    if origin != text.rstrip():
        right = " "
    if origin != text.lstrip():
        left = " "
    return f"{left}{text.strip()}{right}"


def is_vowel(character: str) -> bool:
    """Determines if the given character is a vowel."""
    return character in "aáeéiíoóöőuúüű"


@dataclasses.dataclass
class Syllable:
    """Represents a syllable in a line."""

    text: str
    long: bool = dataclasses.field(init=False)

    def __post_init__(self):
        self.long = self.is_long

    @property
    def is_long(self) -> bool:
        """Determines if the syllable is 'long' based on specific criteria."""
        if not self.text:
            return False
        long_vowels = "áéíóöőúüű"
        double_consonants = ["cs", "dz", "dzs", "gy", "ly", "ny", "sz", "ty", "zs"]
        index, vowel = self.get_vowel()
        if vowel in long_vowels:
            return True
        # Consonants before the vowel in the syllable does not affect the length of the syllable.
        # Therefore, we can ignore them by slicing the text from the vowel.
        # Double consonants does not make the syllable long on its own.
        # The *syllable is long* if there are *more than 2 consonants after the vowel*. *Or* if the *vowel is long*.
        len_from_vowel = len(self.text[index:].replace(" ", ""))
        number_of_double_consonants = sum(
            d_consonant in self.text[index:] for d_consonant in double_consonants
        )
        number_of_letters = len_from_vowel - number_of_double_consonants
        return number_of_letters > 2

    def get_vowel(self) -> t.Tuple[int, str]:
        """Returns the first vowel in the syllable."""
        for i, character in enumerate(self.text):
            if is_vowel(character):
                return i, character
        raise ValueError("No vowel in syllable")

    @property
    def get_repr(self) -> str:
        """Returns the string representation of the syllable."""
        if not self.text:
            return ""
        return "L" if self.is_long else "S"

    def __human_repr__(self):
        return ("{L}" if self.is_long else "{S}") + f"{self.text}| "

    def __machine_repr__(self) -> str:
        return "L" if self.is_long else "S"

    def __repr__(self) -> str:
        return self.__machine_repr__()

    def __str__(self) -> str:
        return self.text

    def to_json(self) -> str:
        return json.dumps(dataclasses.asdict(self))

    def serialize(self) -> dict[str, str]:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class Line:
    """Represents a line in a poem."""

    syllables: list[Syllable]
    line_number: int = 0
    __line_number: int = 0

    def __init__(self, text: str):
        """Initializes the line with the given text, split into syllables."""
        text = re.sub(r"\s+", " ", text)  # Normalize whitespaces
        delimiters = "(a|á|e|é|i|í|o|ó|ö|ő|u|ú|ü|ű)"
        parts = re.split(delimiters, text)
        parts = [strip_if(part) for part in parts if part]
        self.syllables = []
        self.build_syllables(parts)
        self.line_number = type(self).__line_number
        type(self).__line_number += 1

    def build_syllable_list(self, text):
        """Builds a list of Syllable objects from a list of strings."""
        syllable = ""
        for character in text:
            if is_vowel(character):
                if len(syllable) != 0:
                    self.syllables.append(Syllable(syllable))
                syllable = f"{character}"
            elif len(syllable) != 0:
                syllable = syllable + character
        else:  # If the last character is a consonant, append the syllable
            self.syllables.append(Syllable(syllable))

    def build_syllables(self, text):
        buffer_stack: t.List[str] = []
        has_vowel = False

        def push_stack_to_syllables(stack: t.List[str]) -> None:
            """

            :rtype: object
            """
            if stack:
                self.syllables.append(Syllable("".join(stack)))

        def add_to_stack(stack: t.List[str], character: str) -> None:
            stack.append(character)

        def create_new_stack(character: str) -> t.List[str]:
            return [character]

        for character in text:
            if is_vowel(character) and has_vowel:
                push_stack_to_syllables(buffer_stack)
                buffer_stack = create_new_stack(character)
            else:
                add_to_stack(buffer_stack, character)
            has_vowel |= is_vowel(character)
        else:  # nobreak
            push_stack_to_syllables(buffer_stack)

    @property
    def get_repr(self) -> str:
        """Returns the string representation of the line."""
        return "".join(syllable.get_repr for syllable in self.syllables)

    def __repr__(self) -> str:
        return f"L#{self.line_number}" + "".join(map(repr, self.syllables))

    def __str__(self) -> str:
        return "".join(str(syllable) for syllable in self.syllables)

    def serialize(self):
        return {
            "Line#": self.line_number,
            "Syllables:": [syllable.serialize() for syllable in self.syllables],
        }


@dataclasses.dataclass
class Poem:
    lines: t.List[Line] = dataclasses.field(default_factory=list)

    def __init__(self, lines: t.Optional[t.List[Line]]):
        """Initializes the poem with a given list of lines or an empty list."""
        self.lines = lines if lines is not None else []

    def add_line(self, text: str) -> None:
        """Adds a new line to the poem."""
        line = Line(text)
        self.lines.append(line)

    def __getitem__(self, line_number: int) -> Line:
        """Allows indexing to get a specific line."""
        if 0 <= line_number < len(self.lines):
            return self.lines[line_number]
        else:
            raise IndexError("Line number out of range")

    def __iter__(self):
        """Makes the poem iterable over its lines."""
        return iter(self.lines)

    def __len__(self):
        """Returns the number of lines in the poem."""
        return len(self.lines)

    def __repr__(self) -> str:
        return "\n".join(str(line) for line in self.lines)

    def __str__(self) -> str:
        return "\n".join(str(line) for line in self.lines)

    # def to_json(self) -> str:
    #     """Serializes the poem to a JSON string."""
    #     return json.dumps([line.to_json() for line in self.lines], indent=4)

    def serialize(self):
        return {"Lines": [line.serialize() for line in self.lines]}
