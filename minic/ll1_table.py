from typing import Dict, List
from .lexer import Lexer, Token

class ParseError(SyntaxError):
    pass

# ============================================================
# Gramática en forma LL(1) (sin EBNF). ε denota producción vacía
#
# No terminales:
#   Program, PreprocList, MainDef,
#   StmtList, Stmt, Block,
#   Decl, Assign, ReturnStmt,
#   IfStmt, ElseOpt, WhileStmt, ForStmt, ForInit, ForCond, ForStep,
#   Bool, RelP, Expr, ExprP, Term, TermP, Factor
#
# Terminales:
#   PREPROC, INT, TYPE, MAIN, RETURN,
#   ID, NUM, EQ, PLUS, MIN, MUL, DIV, LP, RP, LB, RB, SC,
#   IF, ELSE, WHILE, FOR,
#   LT, LE, GT, GE, EQEQ, NEQ,
#   $
#
# Producciones (resumen):
#   Program     -> PreprocList MainDef
#   PreprocList -> PREPROC PreprocList | ε
#   MainDef     -> INT MAIN LP RP Block
#
#   StmtList    -> Stmt StmtList | ε
#   Stmt        -> Decl SC | Assign SC | ReturnStmt | IfStmt | WhileStmt | ForStmt | Block
#   Block       -> LB StmtList RB
#
#   Decl        -> (INT | TYPE) ID
#   Assign      -> ID EQ Expr
#   ReturnStmt  -> RETURN NUM SC          # (básico: return 0;)
#
#   IfStmt      -> IF LP Bool RP Stmt ElseOpt
#   ElseOpt     -> ELSE Stmt | ε
#
#   WhileStmt   -> WHILE LP Bool RP Stmt
#
#   ForStmt     -> FOR LP ForInit SC ForCond SC ForStep RP Stmt
#   ForInit     -> Decl | Assign | ε
#   ForCond     -> Bool | ε
#   ForStep     -> Assign | ε
#
#   Bool        -> Expr RelP
#   RelP        -> (LT|LE|GT|GE|EQEQ|NEQ) Expr | ε
#
#   Expr        -> Term ExprP
#   ExprP       -> PLUS Term ExprP | MIN Term ExprP | ε
#   Term        -> Factor TermP
#   TermP       -> MUL Factor TermP | DIV Factor TermP | ε
#   Factor      -> ID | NUM | LP Expr RP
# ============================================================

# === LL(1): TERMINALES, EPSILON y TABLA DE PREDICCIÓN ===

EPSILON = 'ε'

TERMINALS = {
    'PREPROC', 'INT', 'TYPE', 'MAIN', 'RETURN',
    'ID', 'NUM', 'EQ', 'PLUS', 'MIN', 'MUL', 'DIV', 'LP', 'RP', 'LB', 'RB', 'SC',
    'IF', 'ELSE', 'WHILE', 'FOR',
    'LT', 'LE', 'GT', 'GE', 'EQEQ', 'NEQ',
    '$'
}

# M[NoTerminal][terminal] = producción (lista de símbolos)
Table: Dict[str, Dict[str, List[str]]] = {
    # Programa: cero o más includes y luego int main() { ... }
    'Program': {
        'PREPROC': ['PreprocList', 'MainDef'],
        'INT':     ['PreprocList', 'MainDef'],
    },

    'PreprocList': {
        'PREPROC': ['PREPROC', 'PreprocList'],
        'INT':     [EPSILON],   # cuando ya llega el 'int' de 'int main()'
    },

    'MainDef': {
        'INT': ['INT', 'MAIN', 'LP', 'RP', 'Block'],  # int main() { ... }
    },

    # Lista de sentencias (dentro de bloques)
    'StmtList': {
        'INT':   ['Stmt', 'StmtList'], 'TYPE': ['Stmt', 'StmtList'],
        'ID':    ['Stmt', 'StmtList'],
        'RETURN':['Stmt', 'StmtList'],
        'IF':    ['Stmt', 'StmtList'], 'WHILE': ['Stmt', 'StmtList'], 'FOR': ['Stmt', 'StmtList'],
        'LB':    ['Stmt', 'StmtList'],
        'RB':    [EPSILON], '$': [EPSILON],
    },

    'Stmt': {
        'INT':    ['Decl', 'SC'],
        'TYPE':   ['Decl', 'SC'],
        'ID':     ['Assign', 'SC'],
        'RETURN': ['ReturnStmt'],
        'IF':     ['IfStmt'],
        'WHILE':  ['WhileStmt'],
        'FOR':    ['ForStmt'],
        'LB':     ['Block'],
    },

    'Block': {
        'LB': ['LB', 'StmtList', 'RB'],
    },

    'Decl': {
        'INT':  ['INT',  'ID'],
        'TYPE': ['TYPE', 'ID'],
    },

    'Assign': {
        'ID': ['ID', 'EQ', 'Expr'],
    },

    'ReturnStmt': {
        'RETURN': ['RETURN', 'NUM', 'SC'],   # básico: return 0;
    },

    # --- if / else ---
    'IfStmt': {
        'IF': ['IF', 'LP', 'Bool', 'RP', 'Stmt', 'ElseOpt'],
    },
    'ElseOpt': {
        'ELSE': ['ELSE', 'Stmt'],
        'INT': [EPSILON], 'TYPE': [EPSILON], 'ID': [EPSILON], 'RETURN': [EPSILON],
        'IF': [EPSILON], 'WHILE': [EPSILON], 'FOR': [EPSILON], 'LB': [EPSILON],
        'RB': [EPSILON], '$': [EPSILON],
    },

    # --- while ---
    'WhileStmt': {
        'WHILE': ['WHILE', 'LP', 'Bool', 'RP', 'Stmt'],
    },

    # --- for (init; cond; step) stmt ---
    'ForStmt': {
        'FOR': ['FOR', 'LP', 'ForInit', 'SC', 'ForCond', 'SC', 'ForStep', 'RP', 'Stmt'],
    },
    'ForInit': {
        'INT':  ['Decl'],
        'TYPE': ['Decl'],
        'ID':   ['Assign'],
        'SC':   [EPSILON],   # for (; cond ; step)
    },
    'ForCond': {
        'ID': ['Bool'], 'NUM': ['Bool'], 'LP': ['Bool'],
        'SC': [EPSILON],     # for (init; ; step)
    },
    'ForStep': {
        'ID': ['Assign'],
        'RP': [EPSILON],     # for (init; cond; )
    },

    # --- booleano relacional simple: Expr [op Expr]? ---
    'Bool': {
        'ID':  ['Expr', 'RelP'],
        'NUM': ['Expr', 'RelP'],
        'LP':  ['Expr', 'RelP'],
    },
    'RelP': {
        'LT':   ['LT',   'Expr'],
        'LE':   ['LE',   'Expr'],
        'GT':   ['GT',   'Expr'],
        'GE':   ['GE',   'Expr'],
        'EQEQ': ['EQEQ', 'Expr'],
        'NEQ':  ['NEQ',  'Expr'],
        # epsilon si no hay operador relacional:
        'RP': [EPSILON], 'SC': [EPSILON], 'RB': [EPSILON], '$': [EPSILON],
        'ELSE':[EPSILON], 'INT':[EPSILON], 'TYPE':[EPSILON], 'ID':[EPSILON],
        'IF':[EPSILON], 'WHILE':[EPSILON], 'FOR':[EPSILON], 'LB':[EPSILON],
        'PLUS':[EPSILON], 'MIN':[EPSILON], 'MUL':[EPSILON], 'DIV':[EPSILON],
    },

    # --- aritmética (igual que tenías) ---
    'Expr': {
        'ID':  ['Term', 'ExprP'],
        'NUM': ['Term', 'ExprP'],
        'LP':  ['Term', 'ExprP'],
    },
    'ExprP': {
        'PLUS': ['PLUS', 'Term', 'ExprP'],
        'MIN':  ['MIN',  'Term', 'ExprP'],
        # epsilon en múltiples entradas válidas de FOLLOW
        'RP':[EPSILON], 'SC':[EPSILON], 'RB':[EPSILON], '$':[EPSILON],
        'ELSE':[EPSILON], 'INT':[EPSILON], 'TYPE':[EPSILON], 'ID':[EPSILON],
        'IF':[EPSILON], 'WHILE':[EPSILON], 'FOR':[EPSILON], 'LB':[EPSILON],
        'LT':[EPSILON], 'LE':[EPSILON], 'GT':[EPSILON], 'GE':[EPSILON], 'EQEQ':[EPSILON], 'NEQ':[EPSILON],
    },
    'Term': {
        'ID':  ['Factor', 'TermP'],
        'NUM': ['Factor', 'TermP'],
        'LP':  ['Factor', 'TermP'],
    },
    'TermP': {
        'MUL':  ['MUL', 'Factor', 'TermP'],
        'DIV':  ['DIV', 'Factor', 'TermP'],
        # epsilon en FOLLOW(TermP)
        'PLUS':[EPSILON], 'MIN':[EPSILON], 'RP':[EPSILON], 'SC':[EPSILON],
        'RB':[EPSILON], '$':[EPSILON], 'ELSE':[EPSILON],
        'INT':[EPSILON], 'TYPE':[EPSILON], 'ID':[EPSILON], 'IF':[EPSILON],
        'WHILE':[EPSILON], 'FOR':[EPSILON], 'LB':[EPSILON],
        'LT':[EPSILON], 'LE':[EPSILON], 'GT':[EPSILON], 'GE':[EPSILON], 'EQEQ':[EPSILON], 'NEQ':[EPSILON],
    },
    'Factor': {
        'ID':  ['ID'],
        'NUM': ['NUM'],
        'LP':  ['LP', 'Expr', 'RP'],
    },
}

def _kind_map(tok: Token) -> str:
    """Mapea el token del lexer a la clave terminal esperada por la tabla LL(1)."""
    return '$' if tok.kind == 'EOF' else tok.kind

def parse_ll1(source: str) -> bool:
    """
    Reconocedor LL(1) table-driven.
    Devuelve True si la cadena es aceptada por la gramática; si no, lanza ParseError.
    """
    tokens: List[Token] = list(Lexer(source))
    stack: List[str] = ['$', 'Program']
    i = 0

    while stack:
        top = stack.pop()
        look = tokens[i] if i < len(tokens) else Token('EOF', '', 1, 1)
        a = _kind_map(look)

        if top == EPSILON:
            continue

        if top in TERMINALS:
            if top == a:
                i += 1
                continue
            raise ParseError(f"Esperaba {top}, recibí {look.kind} ({look.value!r}) en {look.line}:{look.col}")

        row = Table.get(top, {})
        prod = row.get(a)
        if prod is None:
            expected = ", ".join(sorted(row.keys())) or "∅"
            raise ParseError(
                f"No hay producción para {top} con lookahead {look.kind} ({look.value!r}) en {look.line}:{look.col}. "
                f"Esperaba uno de: {expected}"
            )

        for sym in reversed(prod):
            stack.append(sym)

    # aceptación si consumimos todo y el último fue EOF
    if i == len(tokens) and _kind_map(tokens[-1]) == '$':
        return True
    if i < len(tokens):
        extra = tokens[i]
        raise ParseError(f"Tokens extra no consumidos desde {extra.kind} ({extra.value!r}) en {extra.line}:{extra.col}")
    return True
