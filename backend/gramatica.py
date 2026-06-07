"""
gramatica.py - Definicion formal G = (V, Sigma, P, S)
Mas computo de FIRST, FOLLOW y verificacion LL(1)
OE1: Gramatica libre de contexto para IF/WHILE anidadas
"""

from collections import defaultdict

# ---------------------------------------------------------------
#  G = (V, Sigma, P, S)
# ---------------------------------------------------------------

S = "Program"

V = {
    "Program", "Stmt", "IfStmt", "WhileStmt", "AssignStmt",
    "Block", "StmtList", "RestStmtList", "Cond", "RelOp",
    "Expr", "ExprPrime", "AddOp", "Term", "TermPrime", "MulOp", "Factor",
}

Sigma = {
    "id", "num", "if", "then", "else", "while", "do",
    "{", "}", ";", "=", "==", "<", ">", "(", ")",
    "+", "-", "*", "/", "true", "false",
}

P = [
    ("Program",         ["Stmt"]),
    ("Stmt",            ["IfStmt"]),
    ("Stmt",            ["WhileStmt"]),
    ("Stmt",            ["AssignStmt"]),
    ("Stmt",            ["Block"]),
    ("IfStmt",          ["if", "Cond", "then", "Stmt", "else", "Stmt"]),
    ("WhileStmt",       ["while", "Cond", "do", "Stmt"]),
    ("Block",           ["{", "StmtList", "}"]),
    ("StmtList",        ["Stmt", "RestStmtList"]),
    ("RestStmtList",    [";", "Stmt", "RestStmtList"]),
    ("RestStmtList",    []),
    ("AssignStmt",      ["id", "=", "Expr"]),
    ("Cond",            ["Expr", "RelOp", "Expr"]),
    ("Cond",            ["true"]),
    ("Cond",            ["false"]),
    ("RelOp",           ["=="]),
    ("RelOp",           ["<"]),
    ("RelOp",           [">"]),
    ("Expr",            ["Term", "ExprPrime"]),
    ("ExprPrime",       ["AddOp", "Term", "ExprPrime"]),
    ("ExprPrime",       []),
    ("AddOp",           ["+"]),
    ("AddOp",           ["-"]),
    ("Term",            ["Factor", "TermPrime"]),
    ("TermPrime",       ["MulOp", "Factor", "TermPrime"]),
    ("TermPrime",       []),
    ("MulOp",           ["*"]),
    ("MulOp",           ["/"]),
    ("Factor",          ["id"]),
    ("Factor",          ["num"]),
    ("Factor",          ["(", "Expr", ")"]),
]

EPSILON = "ε"
EOF = "$"


def producciones_de(nt):
    return [body for h, body in P if h == nt]


# ---------------------------------------------------------------
#  Computo de FIRST
# ---------------------------------------------------------------

def compute_first():
    first = defaultdict(set)
    # Terminales: FIRST(a) = {a}
    for t in Sigma:
        first[t] = {t}
    # No terminales: inicializar vacio
    for nt in V:
        first[nt] = set()
    # Iterar hasta punto fijo
    changed = True
    while changed:
        changed = False
        for head, body in P:
            # FIRST(epsilon) = {epsilon}
            if not body:
                if EPSILON not in first[head]:
                    first[head].add(EPSILON)
                    changed = True
                continue
            # FIRST(X1 X2 ... Xk)
            all_have_epsilon = True
            for i, sym in enumerate(body):
                if sym in Sigma:
                    first_sym = {sym}
                else:
                    first_sym = first[sym]
                for x in first_sym:
                    if x != EPSILON and x not in first[head]:
                        first[head].add(x)
                        changed = True
                if EPSILON not in first_sym:
                    all_have_epsilon = False
                    break
            if all_have_epsilon:
                if EPSILON not in first[head]:
                    first[head].add(EPSILON)
                    changed = True
    return first


# ---------------------------------------------------------------
#  Computo de FOLLOW
# ---------------------------------------------------------------

def compute_follow(first):
    follow = defaultdict(set)
    for nt in V:
        follow[nt] = set()
    follow[S].add(EOF)  # $ ∈ FOLLOW(S)
    changed = True
    while changed:
        changed = False
        for head, body in P:
            if not body:
                continue
            for i, sym in enumerate(body):
                if sym not in V:
                    continue
                # beta = lo que sigue despues de sym en body
                beta = body[i + 1:]
                # Agregar FIRST(beta) - {epsilon}
                first_beta = compute_first_string(beta, first)
                for x in first_beta:
                    if x != EPSILON and x not in follow[sym]:
                        follow[sym].add(x)
                        changed = True
                # Si epsilon ∈ FIRST(beta), agregar FOLLOW(head)
                if EPSILON in first_beta:
                    for x in follow[head]:
                        if x not in follow[sym]:
                            follow[sym].add(x)
                            changed = True
    return follow


def compute_first_string(body, first):
    if not body:
        return {EPSILON}
    result = set()
    all_eps = True
    for sym in body:
        if sym in Sigma:
            result.add(sym)
            all_eps = False
            break
        else:
            for x in first[sym]:
                if x != EPSILON:
                    result.add(x)
            if EPSILON not in first[sym]:
                all_eps = False
                break
    if all_eps:
        result.add(EPSILON)
    return result


# ---------------------------------------------------------------
#  Verificacion LL(1)
# ---------------------------------------------------------------

def check_ll1(first, follow):
    conflictos = []
    for nt in sorted(V):
        prods = producciones_de(nt)
        for i in range(len(prods)):
            for j in range(i + 1, len(prods)):
                body_i = prods[i]
                body_j = prods[j]
                first_i = compute_first_string(body_i, first)
                first_j = compute_first_string(body_j, first)
                # Conflicto 1: FIRST(alpha_i) ∩ FIRST(alpha_j) != ∅
                common_first = (first_i - {EPSILON}) & (first_j - {EPSILON})
                if common_first:
                    conflictos.append((
                        nt, body_i, body_j,
                        "FIRST-FIRST", common_first
                    ))
                # Conflicto 2: epsilon ∈ FIRST(alpha_i) y FIRST(alpha_j) ∩ FOLLOW(A) != ∅
                if EPSILON in first_i:
                    common_follow = (first_j - {EPSILON}) & follow[nt]
                    if common_follow:
                        conflictos.append((
                            nt, body_i, body_j,
                            "FIRST-FOLLOW", common_follow
                        ))
                if EPSILON in first_j:
                    common_follow = (first_i - {EPSILON}) & follow[nt]
                    if common_follow:
                        conflictos.append((
                            nt, body_i, body_j,
                            "FIRST-FOLLOW (invertido)", common_follow
                        ))
    return conflictos


# ---------------------------------------------------------------
#  Metricas
# ---------------------------------------------------------------

def metricas_gramatica():
    first = compute_first()
    follow = compute_follow(first)
    conflictos = check_ll1(first, follow)
    prod_count = len(P)
    epsilon_prods = sum(1 for _, b in P if not b)
    terminales_en_reglas = set()
    for _, body in P:
        for s in body:
            if s in Sigma:
                terminales_en_reglas.add(s)
    nt_con_epsilon = sum(1 for nt in V if EPSILON in first[nt])

    print("=" * 65)
    print("METRICAS CUANTITATIVAS DE LA GRAMATICA")
    print("=" * 65)
    print(f"\n| Metrica                                | Valor |")
    print(f"|----------------------------------------|-------|")
    print(f"| No terminales (V)                      | {len(V):5d} |")
    print(f"| Terminales (Sigma)                     | {len(Sigma):5d} |")
    print(f"| Producciones (P)                       | {prod_count:5d} |")
    print(f"| Producciones epsilon                   | {epsilon_prods:5d} |")
    print(f"| Terminales usados en reglas            | {len(terminales_en_reglas):5d} |")
    print(f"| No terminales anulables (FIRST con ε)  | {nt_con_epsilon:5d} |")
    print(f"| Conflictos LL(1)                       | {len(conflictos):5d} |")

    print(f"\nFIRST sets:")
    for nt in sorted(V):
        f = sorted(first[nt])
        print(f"  FIRST({nt:15s}) = {{ {', '.join(f)} }}")

    print(f"\nFOLLOW sets:")
    for nt in sorted(V):
        f = sorted(follow[nt])
        print(f"  FOLLOW({nt:15s}) = {{ {', '.join(f)} }}")

    if conflictos:
        print(f"\nCONFLICTOS LL(1) ({len(conflictos)}):")
        for nt, b1, b2, tipo, conjunto in conflictos:
            c1 = " ".join(b1) if b1 else "ε"
            c2 = " ".join(b2) if b2 else "ε"
            print(f"  {nt}: {c1} | {c2}")
            print(f"    Tipo: {tipo}, Conjunto: {conjunto}")
    else:
        print(f"\nLa gramatica es LL(1): No hay conflictos. ✓")

    return first, follow, conflictos


# ---------------------------------------------------------------
#  Cadenas de prueba
# ---------------------------------------------------------------

CADENAS_EJEMPLO = [
    {
        "id": 1,
        "descripcion": "IF-ELSE simple",
        "entrada": "if x == 1 then y = 0 else z = 1",
        "tokens": ["if", "id", "==", "num", "then", "id", "=", "num",
                    "else", "id", "=", "num"],
        "valida": True,
    },
    {
        "id": 2,
        "descripcion": "WHILE simple",
        "entrada": "while x > 0 do x = x - 1",
        "tokens": ["while", "id", ">", "num", "do", "id", "=", "id", "-", "num"],
        "valida": True,
    },
    {
        "id": 3,
        "descripcion": "IF-ELSE anidado",
        "entrada": "if x == 1 then if y == 2 then a = 1 else a = 2 else b = 1",
        "tokens": ["if", "id", "==", "num", "then", "if", "id", "==", "num",
                    "then", "id", "=", "num", "else", "id", "=", "num",
                    "else", "id", "=", "num"],
        "valida": True,
    },
    {
        "id": 4,
        "descripcion": "WHILE con bloque",
        "entrada": "while x > 0 do { s = s + x ; x = x - 1 }",
        "tokens": ["while", "id", ">", "num", "do", "{", "id", "=", "id", "+", "id",
                    ";", "id", "=", "id", "-", "num", "}"],
        "valida": True,
    },
    {
        "id": 5,
        "descripcion": "IF con WHILE anidado",
        "entrada": "if x == 1 then while y > 0 do y = y - 1 else x = 0",
        "tokens": ["if", "id", "==", "num", "then", "while", "id", ">", "num",
                    "do", "id", "=", "id", "-", "num", "else", "id", "=", "num"],
        "valida": True,
    },
]


if __name__ == "__main__":
    metricas_gramatica()
