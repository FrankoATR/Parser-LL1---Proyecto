import pytest
from minic import parse_source, ParseError

INVALID_CASES = [
    "int ;",
    "x = + 2;",
    "float x x;",
    "(x + 1;",
    "1x = 2;",
]

def test_invalid_program_raises():
    for code in INVALID_CASES:
        with pytest.raises(ParseError):
            parse_source(code)
