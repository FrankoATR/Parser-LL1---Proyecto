from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Optional, Iterator
from .lexer import Lexer, Token

class ParseError(SyntaxError):
    pass

@dataclass
class Program:
    stmts: List["Stmt"]

@dataclass
class Decl:
    ttype: str
    name: str

@dataclass
class Assign:
    name: str
    expr: "Expr"

Stmt = Tuple[str, object]

@dataclass
class BinOp:
    op: str
    left: "Expr"
    right: "Expr"

@dataclass
class Num:
    value: str

@dataclass
class Var:
    name: str

Expr = Tuple[str, object]

class Parser:
    def __init__(self, tokens: Iterator[Token]):
        self.tokens = list(tokens)
        self.i = 0

    def peek(self) -> Token:
        return self.tokens[self.i] if self.i < len(self.tokens) else self.tokens[-1]

    def eat(self, kind: str) -> Token:
        t = self.peek()
        if t.kind != kind:
            raise ParseError(f"Esperaba {kind}, recibí {t.kind} ({t.value!r}) en {t.line}:{t.col}")
        self.i += 1
        return t

    def accept(self, kind: str) -> Optional[Token]:
        t = self.peek()
        if t.kind == kind:
            self.i += 1
            return t
        return None

    def parse(self) -> Program:
        stmts: List[Stmt] = []
        while self.peek().kind != "EOF":
            stmts.append(self.parse_stmt())
        return Program(stmts)

    def parse_stmt(self) -> Stmt:
        k = self.peek().kind
        if k == "TYPE":
            decl = self.parse_decl()
            return ("decl", decl)
        elif k == "ID":
            assign = self.parse_assign()
            return ("assign", assign)
        else:
            t = self.peek()
            raise ParseError(f"Inicio de sentencia inválido: {t.kind} ({t.value!r}) en {t.line}:{t.col}")

    def parse_decl(self) -> Decl:
        ttype = self.eat("TYPE").value
        name = self.eat("ID").value
        self.eat("SC")
        return Decl(ttype, name)

    def parse_assign(self) -> Assign:
        name = self.eat("ID").value
        self.eat("EQ")
        expr = self.parse_expr()
        self.eat("SC")
        return Assign(name, expr)

    def parse_expr(self) -> Expr:
        left = self.parse_term()
        while self.peek().kind in ("PLUS", "MIN"):
            op = self.eat(self.peek().kind).value
            right = self.parse_term()
            left = ("binop", BinOp(op, left, right))
        return left

    def parse_term(self) -> Expr:
        left = self.parse_factor()
        while self.peek().kind in ("MUL", "DIV"):
            op = self.eat(self.peek().kind).value
            right = self.parse_factor()
            left = ("binop", BinOp(op, left, right))
        return left

    def parse_factor(self) -> Expr:
        t = self.peek()
        if t.kind == "ID":
            self.eat("ID")
            return ("var", Var(t.value))
        elif t.kind == "NUM":
            self.eat("NUM")
            return ("num", Num(t.value))
        elif t.kind == "LP":
            self.eat("LP")
            expr = self.parse_expr()
            self.eat("RP")
            return expr
        else:
            raise ParseError(f"Factor inválido: {t.kind} ({t.value!r}) en {t.line}:{t.col}")

def parse_source(src: str) -> Program:
    return Parser(Lexer(src)).parse()
