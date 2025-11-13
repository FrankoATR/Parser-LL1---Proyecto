# Parser LL(1) — Fase 1 (Mini-C con includes estrictos + `int main()`)

Este repositorio contiene la implementación de un **analizador sintáctico LL(1) table-driven**
para un mini-subconjunto de C, pensado como entrega de la **Fase 1** del proyecto
TLP02-2025 (Gramáticas formales vs. lenguaje natural).

El parser está compuesto por:

- Un **analizador léxico** (`minic/lexer.py`) que produce tokens de alto nivel
  (palabras clave, identificadores, literales numéricos y de texto, símbolos, etc.).
- Un **reconocedor LL(1) por tabla** (`minic/ll1_table.py`) que implementa la pila y la tabla
  de predicción para una **gramática libre de contexto LL(1)**.
- Un *runner* de demostración (`run_demo.py`) que **revisa todos los archivos** de una carpeta
  (`test_to_parse/` por defecto) y reporta **ACEPTADO/RECHAZADO** por archivo.

El objetivo es mostrar cómo un lenguaje de programación se puede modelar con una CFG LL(1),
mientras que el lenguaje natural excede este modelo.

---

## Estructura del proyecto

```text
minic/
  __init__.py        # exporta parse_ll1 y ParseError
  lexer.py           # analizador léxico (tokens de Mini-C)
  ll1_table.py       # parser LL(1) basado en tabla de predicción + pila

test_to_parse/
  invalido1.c
  invalido2.txt
  invalido3.c
  valido1.c
  valido2.txt
  valido3.c

run_demo.py          # CLI: recorre carpeta y reporta aceptados/rechazados
pytest.ini           # configuración mínima de pytest
requirements.txt     # dependencias del runner (typer, rich)
README.md
```

> El núcleo del parser está totalmente contenido en el paquete `minic/`.
> El resto son utilidades de demo, pruebas y entorno.

---

## Requisitos

- Python **3.12**
- Entorno virtual `.venv` (recomendado)
- Paquetes indicados en `requirements.txt` (solo para el *runner*: `typer` y `rich`)

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
>
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

El *runner*:

- Busca archivos con extensiones `.c` y `.txt`.
- Intenta tokenizar y parsear cada archivo.
- Muestra una tabla con el estado de cada archivo:
  - **ACEPTADO**  → el archivo cumple léxico + gramática LL(1).
  - **RECHAZADO** → hubo un `LexerError` o un `ParseError`.

Ejemplo de salida:

```text
╭────────────── LL(1) Runner ──────────────╮
│ Analizando 6 archivo(s) en test_to_parse │
│ Extensiones: .c, .txt                    │
╰──────────────────────────────────────────╯
Procesando... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00

                                                                    Resultados                                                                    
┏━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃   # ┃ Archivo                     ┃  Estado   ┃ Detalle                                                                                        ┃
┡━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│   1 │ test_to_parse\invalido1.c   │ RECHAZADO │ Carácter inesperado '#' en 1:1                                                                 │
│   2 │ test_to_parse\invalido2.txt │ RECHAZADO │ No hay producción para Program con lookahead ID ('Juan') en 1:1. Esperaba uno de: INT, PREPROC │
│   3 │ test_to_parse\invalido3.c   │ RECHAZADO │ ...                                                                                            │
│   4 │ test_to_parse\valido1.c     │ ACEPTADO  │ -                                                                                              │
│   5 │ test_to_parse\valido2.txt   │ ACEPTADO  │ -                                                                                              │
│   6 │ test_to_parse\valido3.c     │ ACEPTADO  │ -                                                                                              │
└─────┴─────────────────────────────┴───────────┴────────────────────────────────────────────────────────────────────────────────────────────────┘
╭──────────── Resumen ─────────────╮
│ Aceptados: 3/6   Rechazados: 3/6 │
╰──────────────────────────────────╯
```

> El runner considera **RECHAZADO** tanto los errores sintácticos (`ParseError`) como los léxicos
> (`LexerError`), por ejemplo un `#include` mal escrito.

---

## Uso del parser desde código

Además del runner de consola, el parser se puede usar como librería:

```python
from minic.ll1_table import parse_ll1, ParseError

source = """
#include <stdio.h>

int main() {
    int x;
    x = 0 + 1 * (2 + 3);
    return 0;
}
"""

try:
    ok = parse_ll1(source)
    print("Programa aceptado:", ok)
except ParseError as e:
    print("Error sintáctico:", e)
```

La función `parse_ll1(source: str) -> bool` devuelve `True` si el programa es aceptado
y lanza `ParseError` en caso de error sintáctico.

---

## Léxico: tokens definidos por el analizador

El archivo `minic/lexer.py` define una lista de **especificaciones de tokens** (`TOKEN_SPECS`)
y construye un único autómata mediante expresiones regulares. El flujo es típico:

1. Recorrer el código fuente con una expresión regular grande (`MASTER`).
2. Para cada coincidencia:
   - Clasificarla en un tipo de token (`kind`).
   - Ignorar espacios en blanco y signos de puntuación “decorativos”.
   - Llevar seguimiento de línea y columna.

### Tipos de tokens principales

A continuación se listan los tokens **relevantes para la gramática** (es decir, todos los que
aparecen en el conjunto de terminales del parser).

#### Palabras clave de control y tipos

- `PREPROC` → líneas de preprocesador **estrictamente** de la forma  
  `#include <algo>` o `#include "algo"` en una sola línea.
- `INT`   → palabra clave `int`
- `CHAR`  → palabra clave `char`
- `TYPE`  → se usa para `float` (tipo numérico adicional)
- `MAIN`  → identificador especial `main`
- `RETURN` → palabra clave `return`
- `IF`, `ELSE`, `WHILE`, `FOR` → estructuras de control clásicas de C.
- `PRINTF` → llamada a `printf`.

#### Literales e identificadores

- `ID`   → identificadores: `[a-zA-Z_][a-zA-Z_0-9]*`
- `NUM`  → literales numéricos (`123`, `45.67`, etc.)
- `STR`  → cadenas de caracteres en comillas dobles, admitiendo escapes (`"hola\n"`).
- `CHR`  → literales de carácter en comillas simples (`'a'`, `'\n'`).

#### Operadores y separadores

- Aritméticos: `PLUS` (`+`), `MIN` (`-`), `MUL` (`*`), `DIV` (`/`)
- Asignación: `EQ` (`=`)
- Relacionales: `LT` (`<`), `LE` (`<=`), `GT` (`>`), `GE` (`>=`),
  `EQEQ` (`==`), `NEQ` (`!=`)
- Paréntesis y llaves: `LP` (`(`), `RP` (`)`), `LB` (`{`), `RB` (`}`)
- Corchetes: `LSB` (`[`), `RSB` (`]`)
- Puntuación de C: `SC` (`;`), `COMMA` (`,`)

#### Tokens de infraestructura

- `WS` y `NEWLINE` se utilizan para ignorar espacios en blanco y saltos de línea.
- `PUNCT` agrupa caracteres como `.`, `!`, `?` que no afectan a la gramática.
- `MISMATCH` provoca un `LexerError` con el carácter inesperado.
- Al final del análisis léxico se añade de forma explícita un token `EOF`,
  que el parser mapea a la terminal especial `$` (fin de entrada).

---

## Gramática LL(1) implementada

La gramática se especifica en `minic/ll1_table.py` mediante:

- Un conjunto de **terminales** `TERMINALS`.
- Una tabla de predicción `Table: Dict[str, Dict[str, List[str]]]` que codifica
  las **producciones** de la gramática LL(1).
- Un símbolo especial `ε` (epsilon) para indicar la **producción vacía**.

Formalmente, la gramática es una 4-tupla:

> \(G = (V, \Sigma, P, S)\)

donde:

### Conjunto de terminales Σ

```text
Σ = {
  PREPROC,
  INT, TYPE, CHAR, MAIN, RETURN,
  PRINTF,
  ID, NUM, STR, CHR,
  EQ, PLUS, MIN, MUL, DIV,
  LP, RP, LB, RB, LSB, RSB, SC, COMMA,
  IF, ELSE, WHILE, FOR,
  LT, LE, GT, GE, EQEQ, NEQ,
  $
}
```

La terminal `$` representa explícitamente el **fin de entrada** (`EOF`).

### Conjunto de no terminales V

```text
V = {
  Program, PreprocList, MainDef,
  StmtList, Stmt, Block,
  Decl, IntDecl, FloatDecl, DeclInitNumOpt,
  CharDecl, CharDeclRest, CharRestAfterId,
  CharStrInitOpt, CharChrInitOpt,
  Assign, AssignRValue,
  ReturnStmt,
  PrintfStmt, PrintfArgs, PrintfTail,
  PrintfExprList, PrintfExprListP, PrintfExpr,
  IfStmt, ElseOpt,
  WhileStmt,
  ForStmt, ForInit, ForCond, ForStep,
  Bool, RelP,
  Expr, ExprP, Term, TermP, Factor
}
```

### Símbolo inicial S

```text
S = Program
```

### Idea general del lenguaje aceptado

A alto nivel, la gramática describe programas de la forma:

1. Opcionalmente, varias líneas de `#include` bien formadas.
2. Una **única** definición de `int main()` con un bloque `{ ... }`.
3. Dentro del bloque es posible usar:
   - Declaraciones de variables `int`, `float` (`TYPE`) y `char`, con algunas variantes
     de arreglos/punteros para `char`.
   - Asignaciones.
   - Expresiones aritméticas con `+`, `-`, `*`, `/` y paréntesis.
   - Expresiones booleanas con operadores relacionales.
   - `if/else`, `while`, `for`.
   - Llamadas a `printf` con formato `printf("...", exprs...)`.
   - Una instrucción `return` **con un literal numérico** (`return 0;`).

### Producciones P (forma BNF simplificada)

A continuación se listan las producciones extraídas directamente de la tabla LL(1).

#### Estructura global

```text
Program       → PreprocList MainDef

PreprocList   → PREPROC PreprocList
              | ε        (cuando el siguiente token es INT)

MainDef       → INT MAIN LP RP Block
```

#### Sentencias y bloques

```text
StmtList      → Stmt StmtList
              | ε
                (cuando aparece RB o fin de archivo)

Stmt          → Decl SC
              | Assign SC
              | ReturnStmt
              | IfStmt
              | WhileStmt
              | ForStmt
              | Block
              | PrintfStmt SC

Block         → LB StmtList RB
```

#### Declaraciones

```text
Decl          → IntDecl
              | FloatDecl
              | CharDecl

IntDecl       → INT ID DeclInitNumOpt
FloatDecl     → TYPE ID DeclInitNumOpt

DeclInitNumOpt → EQ Expr
               | ε        (sin inicialización)
```

##### Declaraciones de `char`

```text
CharDecl        → CHAR CharDeclRest

CharDeclRest    → MUL ID CharStrInitOpt
                | ID CharRestAfterId

CharRestAfterId → LSB RSB CharStrInitOpt
                | CharChrInitOpt
                | ε

CharStrInitOpt  → EQ STR
                | ε

CharChrInitOpt  → EQ CHR
                | ε
```

Ejemplos admitidos:

```c
char *s = "hola";
char *t;

char nombre[] = "UCA";
char c = 'A';
char d;
```

#### Asignaciones

```text
Assign         → ID EQ AssignRValue

AssignRValue   → Expr
               | STR
               | CHR
```

Por ejemplo:

```c
x = 3 + 4 * 5;
s = "texto";
c = 'Z';
```

#### `return` simplificado

```text
ReturnStmt     → RETURN NUM SC
```

Por simplicidad, el parser solo acepta un literal numérico después de `return`:

```c
return 0;
return 1;
```

No se admite `return x;` ni `return x + 1;` en esta fase.

#### `printf` con formato

```text
PrintfStmt      → PRINTF LP PrintfArgs RP

PrintfArgs      → STR PrintfTail

PrintfTail      → COMMA PrintfExprList
                | ε

PrintfExprList  → PrintfExpr PrintfExprListP

PrintfExprListP → COMMA PrintfExpr PrintfExprListP
                | ε

PrintfExpr      → Expr
                | STR
                | CHR
```

Ejemplos admitidos:

```c
printf("Hola mundo");
printf("x = %d\n", x);
printf("Valores: %d %f %c\n", a, b, c);
printf("Cadena: %s\n", "literal");
```

#### Condicionales y ciclos

```text
IfStmt          → IF LP Bool RP Stmt ElseOpt

ElseOpt         → ELSE Stmt
                | ε

WhileStmt       → WHILE LP Bool RP Stmt

ForStmt         → FOR LP ForInit SC ForCond SC ForStep RP Stmt

ForInit         → Decl
                | Assign
                | ε

ForCond         → Bool
                | ε

ForStep         → Assign
                | ε
```

#### Expresiones booleanas

```text
Bool            → Expr RelP

RelP            → LT   Expr
                | LE   Expr
                | GT   Expr
                | GE   Expr
                | EQEQ Expr
                | NEQ  Expr
                | ε
```

#### Expresiones aritméticas (precedencia clásica)

```text
Expr            → Term ExprP
ExprP           → PLUS Term ExprP
                | MIN  Term ExprP
                | ε

Term            → Factor TermP
TermP           → MUL Factor TermP
                | DIV Factor TermP
                | ε

Factor          → ID
                | NUM
                | LP Expr RP
```

Con esta estructura se respeta la precedencia usual:

- `*` y `/` tienen mayor precedencia que `+` y `-`.
- Las operaciones son asociativas a la izquierda.
- Se permite el uso de paréntesis.

---

## Algoritmo LL(1) table-driven

El archivo `ll1_table.py` implementa el parser con el patrón clásico:

1. Se construye la lista de tokens con el `Lexer`.
2. Se inicializa una pila con `['$', 'Program']`.
3. En cada paso se mira la **cima de la pila** y el **token de entrada actual**:
   - Si la cima es un terminal y coincide con el token, se consume el token.
   - Si la cima es un terminal que **no** coincide, se lanza `ParseError`.
   - Si la cima es un no terminal `A`, se consulta la tabla `Table[A][lookahead]`
     para obtener la producción `A → α` y se reemplaza `A` en la pila por `α`
     (empujando sus símbolos en orden inverso).
   - Si la cima es `ε`, simplemente se descarta.
4. El análisis termina con éxito cuando la pila queda en `$` y se ha consumido
   toda la entrada (el token `EOF`).

La tabla `Table` está construida manualmente a partir de los conjuntos
**FIRST** y **FOLLOW**, asegurando que en cada combinación `(noTerminal, lookahead)`
haya **a lo sumo una producción**, lo que cumple la **propiedad LL(1)**.

---

## Ejemplos de programas

### Programa mínimo válido

```c
#include <stdio.h>

int main() {
    int x;
    x = 0 + 1 * (2 + 3);
    return 0;
}
```

### Programa más completo (aún válido)

```c
#include <stdio.h>
#include "mi_lib.h"

int main() {
    int i;
    float suma = 0.0;
    char *msg = "Resultado:";
    char fin = '\n';

    for (i = 0; i < 10; i = i + 1) {
        suma = suma + i;
    }

    if (suma > 0) {
        printf("%s %f%c", msg, suma, fin);
    } else {
        printf("Nada que mostrar%c", fin);
    }

    return 0;
}
```

### Ejemplos rechazados (por diseño estricto)

```c
// include sin <...> o "..."
#include stdio.h
#include

// main mal formado
int main {
    int ;
    return
}

// return con expresión (no permitido en esta fase)
int main() {
    int x;
    x = 5;
    return x;   // Error: solo se permite RETURN NUM;
}
```
