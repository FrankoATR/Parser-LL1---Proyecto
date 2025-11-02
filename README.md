# Parser LL(1) — Fase 1 (Mini‑C, includes estrictos + `int main()`)

Este repo implementa **solo** el analizador **LL(1) table‑driven** para un mini subconjunto de C.
Incluye:
- Una gramática LL(1) que exige un **léxico** y una **sintaxis** básicos del lenguaje C.
- Un *runner* `run_demo.py` para **recorrer una carpeta** (`test_to_parse/`) y reportar **ACEPTADO/RECHAZADO** por archivo.

---

## Estructura sugerida
```
minic/
  __init__.py        # exporta parse_ll1 y ParseError
  lexer.py           # analizador léxico (includes estrictos)
  ll1_table.py       # reconocedor LL(1) (tabla de predicción + pila)

test_to_parse/
  valido1.c
  valido2.txt
  invalido3.c
  invalido1.c
  invalido2.txt
  invalido3.c

run_demo.py          # CLI: recorre carpeta y reporta aceptados/rechazados
README.md
requirements.txt
```

---

## Requisitos
- Python **3.12**
- Entorno virtual `.venv` (recomendado)
- Paquetes: typer y rich para mostrar resultados de la demo.

### Instalación rápida

#### Windows (PowerShell)
```pwsh
python -m venv .\.venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r .\requirements.txt
```

#### Linux / Mac (bash)
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

> Si copiaste un `.venv` desde otra ubicación y algo quedó apuntando a rutas viejas:
> ```pwsh
> deactivate
> python -m venv .venv --upgrade
> ```

---

## Cómo ejecutar el recorrido de carpeta

### 1) Carpeta por defecto `test_to_parse/`
```bash
python run_demo.py
```

### 2) Carpeta personalizada
```bash
python run_demo.py .\mis_programas
# o
python run_demo.py ./samples
```

**Salida esperada (ejemplo):**
```
╭────────────── LL(1) Runner ──────────────╮
│ Analizando 4 archivo(s) en test_to_parse │
│ Extensiones: .c, .txt                    │
╰──────────────────────────────────────────╯
Procesando... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00

                                                                    Resultados                                                                    
┏━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃   # ┃ Archivo                     ┃  Estado   ┃ Detalle                                                                                        ┃
┡━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│   1 │ test_to_parse\invalido1.c   │ RECHAZADO │ Carácter inesperado '#' en 1:1                                                                 │
│   2 │ test_to_parse\invalido2.txt │ RECHAZADO │ No hay producción para Program con lookahead ID ('Juan') en 1:1. Esperaba uno de: INT, PREPROC │
│   3 │ test_to_parse\valido1.c     │ ACEPTADO  │ -                                                                                              │
│   4 │ test_to_parse\valido2.txt   │ ACEPTADO  │ -                                                                                              │
└─────┴─────────────────────────────┴───────────┴────────────────────────────────────────────────────────────────────────────────────────────────┘
╭──────────── Resumen ─────────────╮
│ Aceptados: 2/4   Rechazados: 2/4 │
╰──────────────────────────────────╯
```

> El *runner* considera **RECHAZADO** tanto los errores sintácticos (**ParseError**) como los léxicos (**LexerError**), p. ej. `#include` inválido.

---

## Gramática (resumen LL(1) actual)
**Extensiones clave:**
- `Program -> PreprocList MainDef`
- `PreprocList -> PREPROC PreprocList | ε (donde PREPROC es una línea #include … válida)`
- `MainDef -> INT MAIN LP RP Block (exige int main() y un bloque)`
- `ReturnStmt -> RETURN NUM SC`
- `Soporte de char y “strings” en C: char *id = "..." y char id[] = "..."`
- `printf("fmt", args...) con argumentos Expr | STR | CHR`

**Resto (simplificado):**
```
StmtList   -> Stmt StmtList | ε
Stmt       -> Decl SC | Assign SC | ReturnStmt | IfStmt | WhileStmt | ForStmt | PrintfStmt SC | Block
Block      -> LB StmtList RB

Decl       -> IntDecl | FloatDecl | CharDecl
IntDecl    -> INT ID DeclInitNumOpt
FloatDecl  -> TYPE ID DeclInitNumOpt
DeclInitNumOpt -> EQ Expr | ε

CharDecl   -> CHAR CharDeclRest
CharDeclRest     -> MUL ID CharStrInitOpt        | ID CharRestAfterId
CharStrInitOpt   -> EQ STR | ε
CharRestAfterId  -> LSB RSB CharStrInitOpt | CharChrInitOpt | ε
CharChrInitOpt   -> EQ CHR | ε

Assign     -> ID EQ AssignRValue
AssignRValue -> Expr | STR | CHR

PrintfStmt -> PRINTF LP PrintfArgs RP
PrintfArgs -> STR PrintfTail
PrintfTail -> COMMA PrintfExprList | ε
PrintfExprList  -> PrintfExpr PrintfExprListP
PrintfExprListP -> COMMA PrintfExpr PrintfExprListP | ε
PrintfExpr      -> Expr | STR | CHR

IfStmt    -> IF LP Bool RP Stmt ElseOpt
ElseOpt   -> ELSE Stmt | ε
WhileStmt -> WHILE LP Bool RP Stmt
ForStmt   -> FOR LP ForInit SC ForCond SC ForStep RP Stmt
ForInit   -> Decl | Assign | ε
ForCond   -> Bool | ε
ForStep   -> Assign | ε

Bool      -> Expr RelP
RelP      -> (LT|LE|GT|GE|EQEQ|NEQ) Expr | ε

Expr      -> Term ExprP
ExprP     -> PLUS Term ExprP | MIN Term ExprP | ε
Term      -> Factor TermP
TermP     -> MUL Factor TermP | DIV Factor TermP | ε
Factor    -> ID | NUM | LP Expr RP
```

**Terminales principales:**
`PREPROC, INT, TYPE, CHAR, MAIN, RETURN, PRINTF, ID, NUM, STR, CHR, EQ, PLUS, MIN, MUL, DIV, LP, RP, LB, RB, LSB, RSB, SC, COMMA, IF, ELSE, WHILE, FOR, LT, LE, GT, GE, EQEQ, NEQ, $`

---

## Ejemplo válido mínimo
```c
#include <stdio.h>

int main() {
    int x;
    x = 0 + 1 * (2 + 3);
    return 0;
}
```

## Ejemplos rechazados (estrictos)
```c
#include stdio.h
#include
int main {
    int ;
    return
}
```

---

## Solución de problemas
- **ModuleNotFoundError: minic** → Ejecuta desde la **raíz** del repo o agrega la raíz al `PYTHONPATH` temporalmente.
- **Copiaste el `.venv`** → repara rutas con `python -m venv .venv --upgrade`.
