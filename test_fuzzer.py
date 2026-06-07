import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parser import tokenizar, Parser, ErrorSintactico

def test_input(entrada, descripcion):
    print(f"\n[Test: {descripcion}]")
    print(f"Entrada: '{entrada}'")
    try:
        tokens = tokenizar(entrada)
        parser = Parser(tokens)
        parser.parse()
        print("Resultado: ACEPTADO (Validado correctamente o Falso Positivo)")
    except ValueError as e:
        print(f"Resultado: RECHAZADO (Error Léxico) -> {e}")
    except ErrorSintactico as e:
        print(f"Resultado: RECHAZADO (Error Sintáctico) -> {e}")
    except Exception as e:
        print(f"Resultado: ERROR DEL SISTEMA (Crash!) -> {type(e).__name__}: {e}")

casos_fuzz = [
    ("3", "Un número suelto (no es una sentencia válida)"),
    ("if 3 then x = 1 else y = 2", "Condición inválida (espera boolean/comparación)"),
    ("x = = 2", "Doble igual en asignación"),
    ("while true do { }", "Bloque vacío"),
    ("x = (1 + 2 * (3 - 4)", "Paréntesis desbalanceado"),
    ("id id id", "Tokens válidos sin sentido gramatical"),
    ("!@#$", "Caracteres no reconocidos por el lexer"),
    ("", "Entrada vacía"),
    ("if true then if true then x=1 else y=2 else z=3", "Anidamiento profundo correcto"),
    ("if true then if true then x=1 else y=2", "Anidamiento sin else exterior (dangling else)"),
    ("x = " + "1 + " * 50 + "1", "Recursión profunda en expresiones"),
    ("x = 1 / 0", "División por cero (sintácticamente válido, semánticamente error)"),
]

print("=== INICIANDO PRUEBAS DE FUZZING / EDGE CASES ===")
for entrada, desc in casos_fuzz:
    test_input(entrada, desc)
