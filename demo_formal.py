from minic import parse_source, ParseError

CODE = """
int x;
x = 3 + 5 * (2 + 1);
float y;
y = x / 2;
"""

if __name__ == "__main__":
    try:
        ast = parse_source(CODE)
        print("Parse formal exitoso: ")
        print(ast)
    except ParseError as e:
        print("❌ Error inesperado en formal:", e)
