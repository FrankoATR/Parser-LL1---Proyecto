import re
from dataclasses import dataclass
from typing import Iterator, List, Tuple

@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    line: int
    col: int

class LexerError(Exception):
    pass

class Lexer:
    TOKEN_SPECS: List[Tuple[str, str]] = [
        ("TYPE",  r"\b(?:int|float|char)\b"),
        ("ID",    r"[a-zA-Z_][a-zA-Z_0-9]*"),
        ("NUM",   r"\d+(?:\.\d+)?"),
        ("EQ",    r"="),
        ("PLUS",  r"\+"),
        ("MIN",   r"-"),
        ("MUL",   r"\*"),
        ("DIV",   r"/"),
        ("LP",    r"\("),
        ("RP",    r"\)"),
        ("SC",    r";"),
        ("PUNCT", r"[.,!?]+"),
        ("WS",    r"[ \t]+"),
        ("NEWLINE", r"\r?\n"),
        ("MISMATCH", r"."),
    ]
    MASTER = re.compile("|".join(f"(?P<{n}>{p})" for n, p in TOKEN_SPECS))

    def __init__(self, source: str):
        self.source = source

    def __iter__(self) -> Iterator[Token]:
        line = 1
        col = 1
        for mo in self.MASTER.finditer(self.source):
            kind = mo.lastgroup
            text = mo.group()
            if kind in ("WS", "PUNCT"):
                col += len(text)
                continue
            if kind == "NEWLINE":
                line += 1
                col = 1
                continue
            if kind == "MISMATCH":
                raise LexerError(f"Carácter inesperado {text!r} en {line}:{col}")
            yield Token(kind, text, line, col)
            col += len(text)
        yield Token("EOF", "", line, col)
