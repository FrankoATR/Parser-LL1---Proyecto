# Fase 1 — CFG vs Lenguaje Natural (mini-C parser + NLP)

Este proyecto compara un **parser descendente** (mini-C) con una **demo NLP** (spaCy) para evidenciar por qué el **lenguaje natural** excede la expresividad de una **CFG** simple.

## Requisitos
- Python **3.12**
- Entorno virtual local (`.venv` recomendado)
- (Opcional) Modelo spaCy en español: `es_core_news_sm`

## Estructura
```
fase1/
  README.md
  requirements.txt
  pytest.ini
  minic/
    __init__.py
    lexer.py
    parser.py
  demo_formal.py
  demo_natural.py
  nlp_demo/
    spacy_demo.py
  tests/
    conftest.py
    test_parser_valid.py
    test_parser_invalid.py
  informe/
    informe.md
  slides/
    slides.md
```

## Instalación

### Windows (PowerShell)
```pwsh
# 1) Crear venv
python -m venv .\.venv

# 2) Activar venv
.\.venv\Scripts\Activate.ps1

# 3) Instalar dependencias
python -m pip install -r .\requirements.txt

# 4) (Opcional) Descargar modelo spaCy en español
python -m spacy download es_core_news_sm
```

### Linux / Mac (bash)
```bash
# 1) Crear venv
python3 -m venv .venv

# 2) Activar venv
source .venv/bin/activate

# 3) Instalar dependencias
python -m pip install -r requirements.txt

# 4) (Opcional) Descargar modelo spaCy en español
python -m spacy download es_core_news_sm
```

## Demos
> Ejecuta desde la **raíz del proyecto**, con el venv **activado**.
```bash
# 1) Código mini-C válido: debe parsear OK
python demo_formal.py

# 2) Oración natural: debe FALLAR (ParseError o similar)
python demo_natural.py

# 3) Demo NLP (si instalaste es_core_news_sm)
python nlp_demo/spacy_demo.py
```
**Salida esperada (ejemplo):**
- `demo_formal.py` → `Parse formal exitoso` y un AST
- `demo_natural.py` → `Fallo esperado con lenguaje natural: Esperaba EQ, …`
- `spacy_demo.py` → tabla de `Tokens / PoS / Dep / Head`

## Pruebas (PyTest)
> Recomendado: correr como **módulo** para evitar launchers antiguos.
```bash
# Ejecutar todo
python -m pytest
```

### Ejecutar pruebas específicas
```bash
python -m pytest tests/test_parser_valid.py -vv
python -m pytest tests/test_parser_invalid.py -vv
```

### Colección de tests (sin ejecutar)
```bash
python -m pytest --collect-only -q
```

### Re-ejecutar solo fallos previos
```bash
python -m pytest --lf -vv
```

## Ejemplos de entradas

**Válidas (mini-C)**
```c
int x;
x = 3 + 5 * (2 + 1);
float y;
y = x / 2;
```

**Inválidas (deben lanzar ParseError)**
```c
int ;
x = + 2;
float x x;
(x + 1;
1x = 2;
```

