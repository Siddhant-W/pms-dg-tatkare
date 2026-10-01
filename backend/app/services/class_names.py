"""Understanding class names like ``6-I``, ``8-II``, ``Class VIII-2`` or ``9B``.

The school's data uses two spellings for the same thing: timetable periods say
``8-II`` (arabic standard, roman division) while a teacher's class-teacher
assignment says ``Class VIII-2`` (roman standard, arabic division). Proxy
ranking needs to know that those are both Standard 8 / Division 2, so names are
parsed into a ``ClassRef`` instead of being compared as strings.
"""
import re
from dataclasses import dataclass

_ROMAN = {
    "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6,
    "VII": 7, "VIII": 8, "IX": 9, "X": 10, "XI": 11, "XII": 12,
}
_ROMAN_BY_VALUE = {v: k for k, v in _ROMAN.items()}

_PATTERN = re.compile(
    r"""^\s*
        (?:class\s+|std\.?\s+|standard\s+)?
        (?P<grade>\d{1,2}|[ivx]{1,4})
        (?:\s*[-/\s]?\s*(?P<division>\d{1,2}|[ivx]{1,4}|[a-z]))?
        \s*$""",
    re.IGNORECASE | re.VERBOSE,
)


def _to_int(token: str) -> int | None:
    if token.isdigit():
        return int(token)
    return _ROMAN.get(token.upper())


@dataclass(frozen=True)
class ClassRef:
    grade: int
    # Numeric divisions are normalised to ints (II == 2); lettered ones (A, B)
    # stay as upper-case strings. None means the name had no division.
    division: int | str | None = None

    @property
    def label(self) -> str:
        if self.division is None:
            return str(self.grade)
        if isinstance(self.division, int):
            return f"{self.grade}-{_ROMAN_BY_VALUE.get(self.division, self.division)}"
        return f"{self.grade}-{self.division}"

    def same_standard(self, other: "ClassRef") -> bool:
        return self.grade == other.grade


def parse_class(name: str | None) -> ClassRef | None:
    """Parse a class name, or return None if it isn't a recognisable class."""
    if not name:
        return None
    match = _PATTERN.match(name)
    if not match:
        return None

    grade = _to_int(match.group("grade"))
    if grade is None or not 1 <= grade <= 12:
        return None

    raw_division = match.group("division")
    division: int | str | None = None
    if raw_division:
        division = _to_int(raw_division)
        if division is None:
            division = raw_division.upper()
    return ClassRef(grade, division)
