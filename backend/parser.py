"""
parser.py - Analizador sintactico por descenso recursivo
OE3: Implementacion del parser con arbol de derivacion y reporte de errores
"""

from gramatica import CADENAS_EJEMPLO


# ---------------------------------------------------------------
#  Arbol de derivacion
# ---------------------------------------------------------------

class NodoAST:
    def __init__(self, tipo, valor=None, hijos=None):
        self.tipo = tipo
        self.valor = valor
        self.hijos = hijos or []

    def agregar(self, hijo):
        self.hijos.append(hijo)
        return hijo

    def mostrar(self, nivel=0, prefijo=""):
        indent = "  " * nivel
        if self.valor is not None:
            print(f"{indent}{prefijo}{self.tipo}({self.valor})")
        else:
            print(f"{indent}{prefijo}{self.tipo}")
        for i, h in enumerate(self.hijos):
            es_ultimo = i == len(self.hijos) - 1
            nuevo_prefijo = "└── " if es_ultimo else "├── "
            h.mostrar(nivel + 1, nuevo_prefijo)


# ---------------------------------------------------------------
#  Parser descendente recursivo
# ---------------------------------------------------------------

class ErrorSintactico(Exception):
    def __init__(self, esperado, encontrado, posicion):
        self.esperado = esperado
        self.encontrado = encontrado
        self.posicion = posicion
        super().__init__(f"Error en posicion {posicion}: se esperaba {esperado}, se encontro '{encontrado}'")


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.errores = []

    def token_actual(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return "EOF"

    def consumir(self, esperado=None):
        tok = self.token_actual()
        if esperado is not None and tok != esperado:
            raise ErrorSintactico(esperado, tok, self.pos)
        self.pos += 1
        return tok

    def hay_tokens(self):
        return self.pos < len(self.tokens)

    # --- Metodos para cada no terminal ---

    def parse_Program(self):
        """Program → Stmt"""
        nodo = NodoAST("Program")
        nodo.agregar(self.parse_Stmt())
        return nodo

    def parse_Stmt(self):
        """Stmt → IfStmt | WhileStmt | AssignStmt | Block"""
        tok = self.token_actual()
        if tok == "if":
            return self.parse_IfStmt()
        elif tok == "while":
            return self.parse_WhileStmt()
        elif tok == "id":
            return self.parse_AssignStmt()
        elif tok == "{":
            return self.parse_Block()
        else:
            raise ErrorSintactico("{if, while, id, {}", tok, self.pos)

    def parse_IfStmt(self):
        """IfStmt → if Cond then Stmt else Stmt"""
        nodo = NodoAST("IfStmt")
        self.consumir("if")
        nodo.agregar(self.parse_Cond())
        self.consumir("then")
        nodo.agregar(self.parse_Stmt())
        self.consumir("else")
        nodo.agregar(self.parse_Stmt())
        return nodo

    def parse_WhileStmt(self):
        """WhileStmt → while Cond do Stmt"""
        nodo = NodoAST("WhileStmt")
        self.consumir("while")
        nodo.agregar(self.parse_Cond())
        self.consumir("do")
        nodo.agregar(self.parse_Stmt())
        return nodo

    def parse_Block(self):
        """Block → { StmtList }"""
        nodo = NodoAST("Block")
        self.consumir("{")
        nodo.agregar(self.parse_StmtList())
        self.consumir("}")
        return nodo

    def parse_StmtList(self):
        """StmtList → Stmt RestStmtList"""
        nodo = NodoAST("StmtList")
        nodo.agregar(self.parse_Stmt())
        nodo.agregar(self.parse_RestStmtList())
        return nodo

    def parse_RestStmtList(self):
        """RestStmtList → ; Stmt RestStmtList | ε"""
        nodo = NodoAST("RestStmtList")
        if self.token_actual() == ";":
            self.consumir(";")
            nodo.agregar(NodoAST(";"))
            nodo.agregar(self.parse_Stmt())
            nodo.agregar(self.parse_RestStmtList())
        else:
            nodo.agregar(NodoAST("ε"))
        return nodo

    def parse_AssignStmt(self):
        """AssignStmt → id = Expr"""
        nodo = NodoAST("AssignStmt")
        self.consumir("id")
        nodo.agregar(NodoAST("id"))
        self.consumir("=")
        nodo.agregar(NodoAST("="))
        nodo.agregar(self.parse_Expr())
        return nodo

    def parse_Cond(self):
        """Cond → Expr RelOp Expr | true | false"""
        nodo = NodoAST("Cond")
        tok = self.token_actual()
        if tok == "true":
            self.consumir("true")
            nodo.agregar(NodoAST("true"))
        elif tok == "false":
            self.consumir("false")
            nodo.agregar(NodoAST("false"))
        else:
            nodo.agregar(self.parse_Expr())
            nodo.agregar(self.parse_RelOp())
            nodo.agregar(self.parse_Expr())
        return nodo

    def parse_RelOp(self):
        """RelOp → == | < | >"""
        nodo = NodoAST("RelOp")
        tok = self.token_actual()
        if tok in ("==", "<", ">"):
            self.consumir(tok)
            nodo.agregar(NodoAST(tok))
        else:
            raise ErrorSintactico("{==, <, >}", tok, self.pos)
        return nodo

    def parse_Expr(self):
        """Expr → Term ExprPrime"""
        nodo = NodoAST("Expr")
        nodo.agregar(self.parse_Term())
        nodo.agregar(self.parse_ExprPrime())
        return nodo

    def parse_ExprPrime(self):
        """ExprPrime → AddOp Term ExprPrime | ε"""
        nodo = NodoAST("ExprPrime")
        if self.token_actual() in ("+", "-"):
            nodo.agregar(self.parse_AddOp())
            nodo.agregar(self.parse_Term())
            nodo.agregar(self.parse_ExprPrime())
        else:
            nodo.agregar(NodoAST("ε"))
        return nodo

    def parse_AddOp(self):
        """AddOp → + | -"""
        nodo = NodoAST("AddOp")
        tok = self.token_actual()
        if tok in ("+", "-"):
            self.consumir(tok)
            nodo.agregar(NodoAST(tok))
        else:
            raise ErrorSintactico("{+, -}", tok, self.pos)
        return nodo

    def parse_Term(self):
        """Term → Factor TermPrime"""
        nodo = NodoAST("Term")
        nodo.agregar(self.parse_Factor())
        nodo.agregar(self.parse_TermPrime())
        return nodo

    def parse_TermPrime(self):
        """TermPrime → MulOp Factor TermPrime | ε"""
        nodo = NodoAST("TermPrime")
        if self.token_actual() in ("*", "/"):
            nodo.agregar(self.parse_MulOp())
            nodo.agregar(self.parse_Factor())
            nodo.agregar(self.parse_TermPrime())
        else:
            nodo.agregar(NodoAST("ε"))
        return nodo

    def parse_MulOp(self):
        """MulOp → * | /"""
        nodo = NodoAST("MulOp")
        tok = self.token_actual()
        if tok in ("*", "/"):
            self.consumir(tok)
            nodo.agregar(NodoAST(tok))
        else:
            raise ErrorSintactico("{*, /}", tok, self.pos)
        return nodo

    def parse_Factor(self):
        """Factor → id | num | ( Expr )"""
        nodo = NodoAST("Factor")
        tok = self.token_actual()
        if tok == "id":
            self.consumir("id")
            nodo.agregar(NodoAST("id"))
        elif tok == "num":
            self.consumir("num")
            nodo.agregar(NodoAST("num"))
        elif tok == "(":
            self.consumir("(")
            nodo.agregar(NodoAST("("))
            nodo.agregar(self.parse_Expr())
            self.consumir(")")
            nodo.agregar(NodoAST(")"))
        else:
            raise ErrorSintactico("{id, num, (}", tok, self.pos)
        return nodo

    def parse(self):
        """Punto de entrada: analiza la entrada completa."""
        arbol = self.parse_Program()
        if self.hay_tokens():
            raise ErrorSintactico("EOF", self.token_actual(), self.pos)
        return arbol


# ---------------------------------------------------------------
#  Tokenizador simplificado
# ---------------------------------------------------------------

def tokenizar(entrada):
    """Convierte una cadena de entrada en una lista de tokens."""
    import re
    tokens = []
    patrones = [
        ("if", r"\bif\b"),
        ("then", r"\bthen\b"),
        ("else", r"\belse\b"),
        ("while", r"\bwhile\b"),
        ("do", r"\bdo\b"),
        ("true", r"\btrue\b"),
        ("false", r"\bfalse\b"),
        ("==", r"=="),
        ("<", r"<"),
        (">", r">"),
        ("=", r"="),
        ("{", r"\{"),
        ("}", r"\}"),
        (";", r";"),
        ("(", r"\("),
        (")", r"\)"),
        ("+", r"\+"),
        ("-", r"-"),
        ("*", r"\*"),
        ("/", r"/"),
        ("num", r"\d+"),
        ("id", r"[a-zA-Z_]\w*"),
    ]
    pos = 0
    while pos < len(entrada):
        if entrada[pos].isspace():
            pos += 1
            continue
        match = None
        for nombre, patron in patrones:
            m = re.match(patron, entrada[pos:])
            if m:
                match = (nombre, m)
                break
        if match:
            nombre, m = match
            tokens.append(nombre)
            pos += m.end()
        else:
            raise ValueError(f"Caracter inesperado en posicion {pos}: '{entrada[pos]}'")
    return tokens


# ---------------------------------------------------------------
#  Pruebas
# ---------------------------------------------------------------

def analizar(entrada):
    """Funcion de alto nivel: tokeniza, parsea, retorna arbol."""
    print(f"\n--- Analizando: {entrada} ---")
    try:
        tokens = tokenizar(entrada)
        print(f"Tokens: {tokens}")
        parser = Parser(tokens)
        arbol = parser.parse()
        print("RESULTADO: VALIDA ✓")
        print("\nArbol de derivacion:")
        arbol.mostrar()
        return True, arbol
    except ErrorSintactico as e:
        print(f"RESULTADO: INVALIDA ✗")
        print(f"Error sintactico: {e}")
        return False, str(e)
    except ValueError as e:
        print(f"RESULTADO: INVALIDA ✗")
        print(f"Error lexico: {e}")
        return False, str(e)


# ---------------------------------------------------------------
#  Suite de pruebas
# ---------------------------------------------------------------

CASOS_PRUEBA = [
    # (entrada, deberia_ser_valida, descripcion)
    # --- Casos validos ---
    ("if x == 1 then y = 0 else z = 1", True,
     "IF-ELSE simple"),
    ("while x > 0 do x = x - 1", True,
     "WHILE simple"),
    ("if x == 1 then if y == 2 then a = 1 else a = 2 else b = 1", True,
     "IF-ELSE anidado"),
    ("while x > 0 do { s = s + x ; x = x - 1 }", True,
     "WHILE con bloque"),
    ("if x == 1 then while y > 0 do y = y - 1 else x = 0", True,
     "IF con WHILE anidado"),
    ("{ x = 5 ; y = x + 3 }", True,
     "Bloque con dos asignaciones"),
    ("x = 42", True, "Asignacion simple"),
    ("if true then x = 1 else x = 2", True,
     "IF con condicion booleana 'true'"),
    ("while x < 10 do x = x * 2", True,
     "WHILE con multiplicacion"),
    ("if x > 0 then { a = 1 ; b = 2 } else { a = 3 ; b = 4 }", True,
     "IF-ELSE con bloques en ambas ramas"),
    # --- Casos invalidos ---
    ("if x == 1 then y = 0", False,
     "IF sin ELSE (dangling-else)"),
    ("while x > 0", False,
     "WHILE sin cuerpo"),
    ("x =", False,
     "Asignacion sin expresion"),
    ("if x == then y = 1 else z = 2", False,
     "Condicion incompleta (falta expr)"),
    ("{ x = 1 ; y = 2", False,
     "Bloque sin cerrar"),
    ("x + 1", False,
     "Expresion sin asignacion"),
    ("if x == 1 then else y = 0", False,
     "IF sin sentencia en then"),
    ("while do x = 1", False,
     "WHILE sin condicion"),
]


def ejecutar_suite():
    """Ejecuta todos los casos de prueba y muestra metricas."""
    print("=" * 65)
    print("SUITE DE PRUEBAS DEL ANALIZADOR SINTACTICO")
    print("=" * 65)

    resultados = []
    for entrada, esperado, desc in CASOS_PRUEBA:
        try:
            tokens = tokenizar(entrada)
            parser = Parser(tokens)
            arbol = parser.parse()
            resultado = True
        except (ErrorSintactico, ValueError) as e:
            resultado = False
        correcto = (resultado == esperado)
        resultados.append(correcto)
        estado = "✓" if correcto else "✗"
        print(f"\n{estado} [{desc}]")
        print(f"   Entrada: {entrada}")
        v_esperado = "valida" if esperado else "invalida"
        v_obtenido = "valida" if resultado else "invalida"
        print(f"   Esperado: {v_esperado} | Obtenido: {v_obtenido}")

    total = len(resultados)
    aciertos = sum(resultados)
    pct = (aciertos / total) * 100

    print("\n" + "=" * 65)
    print("RESUMEN DE RESULTADOS")
    print("=" * 65)
    print(f"\n  | Metrica                         | Valor     |")
    print(f"  |---------------------------------|-----------|")
    print(f"  | Total casos de prueba           | {total:9d} |")
    print(f"  | Aciertos                        | {aciertos:9d} |")
    print(f"  | Errores                         | {total - aciertos:9d} |")
    print(f"  | Porcentaje de acierto           | {pct:8.2f}% |")

    tipos_error = {
        "token inesperado": 0,
        "fin de entrada prematuro": 0,
        "error lexico": 0,
        "otro": 0,
    }
    for entrada, esperado, desc in CASOS_PRUEBA:
        if not esperado:
            try:
                tokens = tokenizar(entrada)
                parser = Parser(tokens)
                arbol = parser.parse()
            except ErrorSintactico as e:
                msg = str(e)
                # Clasificar el error
                pass
            except ValueError as e:
                tipos_error["error lexico"] += 1
            except Exception:
                tipos_error["otro"] += 1

    print(f"\n  Tipos de error detectados:")
    print(f"  | Tipo de error                   | Cantidad |")
    print(f"  |---------------------------------|----------|")
    for tipo, cant in tipos_error.items():
        if cant > 0:
            print(f"  | {tipo:31s} | {cant:8d} |")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        entrada = " ".join(sys.argv[1:])
        analizar(entrada)
    else:
        ejecutar_suite()
