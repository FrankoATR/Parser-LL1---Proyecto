from minic import parse_source

def test_valid_program_parses():
    src = "int x; x = 3 + 5 * (2 + 1);"
    ast = parse_source(src)
    assert ast.stmts and len(ast.stmts) == 2
