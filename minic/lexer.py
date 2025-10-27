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
        # --- Preprocesador (#include ...) -> consumir la línea completa ---
        ("PREPROC", r"\#include\s*(<[^>\r\n]+>|\"[^\"\r\n]+\")"),

        # --- Palabras clave específicas para main/retorno ---
        ("INT",    r"\bint\b"),
        ("MAIN",   r"\bmain\b"),
        ("RETURN", r"\breturn\b"),

        # --- Palabras clave de control (si ya las usabas) ---
        ("IF",     r"\bif\b"),
        ("ELSE",   r"\belse\b"),
        ("WHILE",  r"\bwhile\b"),
        ("FOR",    r"\bfor\b"),

        # --- Tipos restantes (dejamos int separado) ---
        ("TYPE",   r"\b(?:float|char)\b"),

        # --- Identificadores y números ---
        ("ID",    r"[a-zA-Z_][a-zA-Z_0-9]*"),
        ("NUM",   r"\d+(?:\.\d+)?"),

        # --- Operadores relacionales (dobles primero) ---
        ("LE",    r"<="),
        ("GE",    r">="),
        ("EQEQ",  r"=="),
        ("NEQ",   r"!="),
        ("LT",    r"<"),
        ("GT",    r">"),

        # --- Asignación y aritméticos ---
        ("EQ",    r"="),
        ("PLUS",  r"\+"),
        ("MIN",   r"-"),
        ("MUL",   r"\*"),
        ("DIV",   r"/"),

        # --- Paréntesis y llaves ---
        ("LP",    r"\("),
        ("RP",    r"\)"),
        ("LB",    r"\{"),
        ("RB",    r"\}"),

        # --- Puntuación / separadores ---
        ("SC",    r";"),

        # --- Ruido que ignoramos ---
        ("PUNCT",   r"[.,!?]+"),
        ("WS",      r"[ \t]+"),
        ("NEWLINE", r"\r?\n"),

        # --- Cualquier otro carácter ---
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

            # Ignorar espacios y puntuación suelta (.,!?)
            if kind in ("WS", "PUNCT"):
                col += len(text)
                continue

            # Manejo de nueva línea
            if kind == "NEWLINE":
                line += 1
                col = 1
                continue

            # Error léxico
            if kind == "MISMATCH":
                raise LexerError(f"Carácter inesperado {text!r} en {line}:{col}")

            # Emitimos token normal (incluye PREPROC como línea entera)
            yield Token(kind, text, line, col)
            col += len(text)

        yield Token("EOF", "", line, col)
