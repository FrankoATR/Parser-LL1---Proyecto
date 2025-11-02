from typing import Dict, List
from .lexer import Lexer, Token

class ParseError(SyntaxError):
    pass

EPSILON = 'ε'

TERMINALS = {
    'PREPROC', 'INT', 'TYPE', 'CHAR', 'MAIN', 'RETURN',
    'PRINTF',
    'ID', 'NUM', 'STR', 'CHR',
    'EQ', 'PLUS', 'MIN', 'MUL', 'DIV',
    'LP', 'RP', 'LB', 'RB', 'LSB', 'RSB', 'SC', 'COMMA',
    'IF', 'ELSE', 'WHILE', 'FOR',
    'LT', 'LE', 'GT', 'GE', 'EQEQ', 'NEQ',
    '$'
}

Table: Dict[str, Dict[str, List[str]]] = {
    'Program': {
        'PREPROC': ['PreprocList', 'MainDef'],
        'INT':     ['PreprocList', 'MainDef'],
    },

    'PreprocList': {
        'PREPROC': ['PREPROC', 'PreprocList'],
        'INT':     [EPSILON],
    },

    'MainDef': {
        'INT': ['INT', 'MAIN', 'LP', 'RP', 'Block'],
    },

    'StmtList': {
        'INT':    ['Stmt', 'StmtList'],
        'TYPE':   ['Stmt', 'StmtList'],
        'CHAR':   ['Stmt', 'StmtList'],
        'ID':     ['Stmt', 'StmtList'],
        'RETURN': ['Stmt', 'StmtList'],
        'IF':     ['Stmt', 'StmtList'],
        'WHILE':  ['Stmt', 'StmtList'],
        'FOR':    ['Stmt', 'StmtList'],
        'LB':     ['Stmt', 'StmtList'],
        'PRINTF': ['Stmt', 'StmtList'],
        'RB':     [EPSILON],
        '$':      [EPSILON],
    },

    'Stmt': {
        'INT':    ['Decl', 'SC'],
        'TYPE':   ['Decl', 'SC'],
        'CHAR':   ['Decl', 'SC'],
        'ID':     ['Assign', 'SC'],
        'RETURN': ['ReturnStmt'],
        'IF':     ['IfStmt'],
        'WHILE':  ['WhileStmt'],
        'FOR':    ['ForStmt'],
        'LB':     ['Block'],
        'PRINTF': ['PrintfStmt', 'SC'],
    },

    'Block': {
        'LB': ['LB', 'StmtList', 'RB'],
    },

    'Decl': {
        'INT':  ['IntDecl'],
        'TYPE': ['FloatDecl'],
        'CHAR': ['CharDecl'],
    },

    'IntDecl': {
        'INT': ['INT', 'ID', 'DeclInitNumOpt'],
    },
    'FloatDecl': {
        'TYPE': ['TYPE', 'ID', 'DeclInitNumOpt'],
    },
    'DeclInitNumOpt': {
        'EQ': ['EQ', 'Expr'],
        'SC': [EPSILON],
    },

    'CharDecl': {
        'CHAR': ['CHAR', 'CharDeclRest'],
    },
    'CharDeclRest': {
        'MUL': ['MUL', 'ID', 'CharStrInitOpt'],
        'ID':  ['ID', 'CharRestAfterId'],
    },
    'CharRestAfterId': {
        'LSB': ['LSB', 'RSB', 'CharStrInitOpt'],
        'EQ':  ['CharChrInitOpt'],
        'SC':  [EPSILON],
    },
    'CharStrInitOpt': {
        'EQ': ['EQ', 'STR'],
        'SC': [EPSILON],
    },
    'CharChrInitOpt': {
        'EQ': ['EQ', 'CHR'],
        'SC': [EPSILON],
    },

    'Assign': {
        'ID': ['ID', 'EQ', 'AssignRValue'],
    },
    'AssignRValue': {
        'ID':  ['Expr'],
        'NUM': ['Expr'],
        'LP':  ['Expr'],
        'STR': ['STR'],
        'CHR': ['CHR'],
    },

    'ReturnStmt': {
        'RETURN': ['RETURN', 'NUM', 'SC'],
    },

    'PrintfStmt': {
        'PRINTF': ['PRINTF', 'LP', 'PrintfArgs', 'RP'],
    },
    'PrintfArgs': {
        'STR': ['STR', 'PrintfTail'],
    },
    'PrintfTail': {
        'COMMA': ['COMMA', 'PrintfExprList'],
        'RP':    [EPSILON],
    },
    'PrintfExprList': {
        'ID':  ['PrintfExpr', 'PrintfExprListP'],
        'NUM': ['PrintfExpr', 'PrintfExprListP'],
        'LP':  ['PrintfExpr', 'PrintfExprListP'],
        'STR': ['PrintfExpr', 'PrintfExprListP'],
        'CHR': ['PrintfExpr', 'PrintfExprListP'],
    },
    'PrintfExprListP': {
        'COMMA': ['COMMA', 'PrintfExpr', 'PrintfExprListP'],
        'RP':    [EPSILON],
    },
    'PrintfExpr': {
        'ID':  ['Expr'],
        'NUM': ['Expr'],
        'LP':  ['Expr'],
        'STR': ['STR'],
        'CHR': ['CHR'],
    },

    'IfStmt': {
        'IF': ['IF', 'LP', 'Bool', 'RP', 'Stmt', 'ElseOpt'],
    },
    'ElseOpt': {
        'ELSE': ['ELSE', 'Stmt'],
        'INT': [EPSILON], 'TYPE': [EPSILON], 'CHAR':[EPSILON],
        'ID': [EPSILON], 'RETURN': [EPSILON], 'IF': [EPSILON],
        'WHILE': [EPSILON], 'FOR': [EPSILON], 'LB': [EPSILON],
        'PRINTF': [EPSILON], 'RB': [EPSILON], '$': [EPSILON],
    },

    'WhileStmt': {
        'WHILE': ['WHILE', 'LP', 'Bool', 'RP', 'Stmt'],
    },

    'ForStmt': {
        'FOR': ['FOR', 'LP', 'ForInit', 'SC', 'ForCond', 'SC', 'ForStep', 'RP', 'Stmt'],
    },
    'ForInit': {
        'INT':    ['Decl'],
        'TYPE':   ['Decl'],
        'CHAR':   ['Decl'],
        'ID':     ['Assign'],
        'SC':     [EPSILON],
    },
    'ForCond': {
        'ID': ['Bool'], 'NUM': ['Bool'], 'LP': ['Bool'],
        'SC': [EPSILON],
    },
    'ForStep': {
        'ID': ['Assign'],
        'RP': [EPSILON],
    },

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
        'RP': [EPSILON], 'SC': [EPSILON], 'RB': [EPSILON], '$': [EPSILON],
        'ELSE':[EPSILON], 'INT':[EPSILON], 'TYPE':[EPSILON], 'CHAR':[EPSILON],
        'ID':[EPSILON], 'IF':[EPSILON], 'WHILE':[EPSILON], 'FOR':[EPSILON],
        'LB':[EPSILON], 'PRINTF':[EPSILON],
        'PLUS':[EPSILON], 'MIN':[EPSILON], 'MUL':[EPSILON], 'DIV':[EPSILON],
    },

    'Expr': {
        'ID':  ['Term', 'ExprP'],
        'NUM': ['Term', 'ExprP'],
        'LP':  ['Term', 'ExprP'],
    },
    'ExprP': {
        'PLUS': ['PLUS', 'Term', 'ExprP'],
        'MIN':  ['MIN',  'Term', 'ExprP'],
        'RP':[EPSILON], 'SC':[EPSILON], 'RB':[EPSILON], '$':[EPSILON],
        'ELSE':[EPSILON], 'INT':[EPSILON], 'TYPE':[EPSILON], 'CHAR':[EPSILON], 'ID':[EPSILON],
        'IF':[EPSILON], 'WHILE':[EPSILON], 'FOR':[EPSILON], 'LB':[EPSILON], 'PRINTF':[EPSILON],
        'LT':[EPSILON], 'LE':[EPSILON], 'GT':[EPSILON], 'GE':[EPSILON], 'EQEQ':[EPSILON], 'NEQ':[EPSILON],
        'COMMA':[EPSILON],
    },
    'Term': {
        'ID':  ['Factor', 'TermP'],
        'NUM': ['Factor', 'TermP'],
        'LP':  ['Factor', 'TermP'],
    },
    'TermP': {
        'MUL':  ['MUL', 'Factor', 'TermP'],
        'DIV':  ['DIV', 'Factor', 'TermP'],
        'PLUS':[EPSILON], 'MIN':[EPSILON], 'RP':[EPSILON], 'SC':[EPSILON],
        'RB':[EPSILON], '$':[EPSILON], 'ELSE':[EPSILON], 'COMMA':[EPSILON],
        'INT':[EPSILON], 'TYPE':[EPSILON], 'CHAR':[EPSILON], 'ID':[EPSILON], 'IF':[EPSILON],
        'WHILE':[EPSILON], 'FOR':[EPSILON], 'LB':[EPSILON], 'PRINTF':[EPSILON],
        'LT':[EPSILON], 'LE':[EPSILON], 'GT':[EPSILON], 'GE':[EPSILON], 'EQEQ':[EPSILON], 'NEQ':[EPSILON],
    },
    'Factor': {
        'ID':  ['ID'],
        'NUM': ['NUM'],
        'LP':  ['LP', 'Expr', 'RP'],
    },
}

def _kind_map(tok: Token) -> str:
    return '$' if tok.kind == 'EOF' else tok.kind

def parse_ll1(source: str) -> bool:
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

    if i == len(tokens) and _kind_map(tokens[-1]) == '$':
        return True
    if i < len(tokens):
        extra = tokens[i]
        raise ParseError(f"Tokens extra no consumidos desde {extra.kind} ({extra.value!r}) en {extra.line}:{extra.col}")
    return True
