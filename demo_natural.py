from minic import parse_source, ParseError
from minic.lexer import LexerError

SENTENCE = "Juan come manzanas."

if __name__ == "__main__":
    try:
        ast = parse_source(SENTENCE)
        print("Esto no debería parsear como C:", ast)
    except (ParseError, LexerError) as e:
        print("Fallo esperado con lenguaje natural:")
        print("   ", e)
