import sys, os
# Agrega la raíz del proyecto (…/fase1) al sys.path para que "minic" se pueda importar en los tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
