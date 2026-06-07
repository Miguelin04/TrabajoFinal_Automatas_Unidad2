"""
pda.py - Automata de Pila (PDA) equivalente a la gramatica G
OE2: Modelado del PDA con estados, transiciones y condiciones de aceptacion
"""

from gramatica import V, Sigma, P, S, EPSILON, EOF, producciones_de, compute_first, compute_first_string, compute_follow


# ---------------------------------------------------------------
#  PDA: M = (Q, Sigma, Gamma, delta, q0, Z0, F)
# ---------------------------------------------------------------

# Q — Estados
Q = {"q0", "q1", "qf"}

# Estado inicial
q0 = "q0"
qf = "qf"

# Marcador de fondo de pila
Z0 = "Z0"

# Gamma — Alfabeto de pila = V ∪ Sigma ∪ {Z0}
Gamma = V | Sigma | {Z0}

# Delta — Transiciones
# Formato: (origen, entrada, tope_pila) -> (destino, [simbolos_a_apilar])

delta = []

# 1. Inicial: (q0, ε, ε) -> (q1, S$)
delta.append(("q0", EPSILON, EPSILON, "q1", [S, Z0]))

# 2. Expansion: (q1, ε, A) -> (q1, α) por cada produccion A -> α
for head, body in P:
    delta.append(("q1", EPSILON, head, "q1", list(body)))  # body vacio = epsilon

# 3. Matching: (q1, a, a) -> (q1, ε) por cada terminal a
for t in Sigma:
    delta.append(("q1", t, t, "q1", []))

# 4. Aceptacion: (q1, ε, Z0) -> (qf, ε)
delta.append(("q1", EPSILON, Z0, "qf", []))


# ---------------------------------------------------------------
#  Simulacion del PDA (top-down, deterministico LL(1))
# ---------------------------------------------------------------

def simular_pda(tokens):
    """Simula el PDA deterministicamente usando FIRST/FOLLOW para decidir."""
    first = compute_first()
    follow = compute_follow(first)

    pila = [Z0, S]  # $ debajo, S arriba
    entrada = list(tokens) + [EOF]
    idx = 0
    estado = "q1"
    configs = [("q1", idx, list(pila))]

    while True:
        tope = pila[-1] if pila else EPSILON
        actual = entrada[idx]

        # Aceptacion
        if tope == Z0 and actual == EOF:
            pila.pop()
            estado = "qf"
            configs.append(("qf", idx, list(pila)))
            break

        aplicada = False

        # Expansion: tope es no terminal
        if tope in V:
            cuerpos = producciones_de(tope)
            elegido = None
            for cuerpo in cuerpos:
                first_cuerpo = compute_first_string(cuerpo, first)
                if actual in first_cuerpo:
                    elegido = cuerpo
                    break
            if elegido is None:
                for cuerpo in cuerpos:
                    if not cuerpo:  # epsilon
                        if actual in follow.get(tope, set()):
                            elegido = cuerpo
                            break
            if elegido is not None:
                pila.pop()
                for sym in reversed(elegido):
                    pila.append(sym)
                aplicada = True
                configs.append(("q1", idx, list(pila)))

        # Match: tope es terminal y coincide con entrada
        if not aplicada and tope == actual:
            pila.pop()
            idx += 1
            aplicada = True
            configs.append(("q1", idx, list(pila)))

        if not aplicada:
            break

    aceptado = (estado == "qf")
    return aceptado, configs


def mostrar_pda():
    """Muestra la definicion formal del PDA."""
    print("=" * 65)
    print("PDA: M = (Q, Sigma, Gamma, delta, q0, Z0, F)")
    print("=" * 65)

    print(f"\nEstados (Q, {len(Q)}):")
    for q in sorted(Q):
        print(f"  {q}")
    print(f"  Estado inicial: q0 = {q0}")
    print(f"  Estado final:   qf = {qf}")

    print(f"\nAlfabeto de entrada (Sigma, {len(Sigma)}):")
    print(f"  {', '.join(sorted(Sigma))}")

    print(f"\nAlfabeto de pila (Gamma, {len(Gamma)}):")
    print(f"  No terminales: {', '.join(sorted(V))}")
    print(f"  Terminales:    {', '.join(sorted(Sigma))}")
    print(f"  Marcador:      {Z0}")

    print(f"\nTransiciones (delta, {len(delta)}):")
    print(f"  {'#':3s} | {'Origen':6s} | {'Entrada':8s} | {'Tope':8s} | {'Destino':7s} | {'Apilar':20s} | Descripcion")
    print(f"  {'-'*3}-+-{'-'*6}-+-{'-'*8}-+-{'-'*8}-+-{'-'*7}-+-{'-'*20}-+-" + "-" * 30)
    for i, (o, e, t, d, a) in enumerate(delta, 1):
        apilar = " ".join(a) if a else "ε"
        if o == "q0" and e == EPSILON and t == EPSILON:
            desc = "Inicial: apilar S"
        elif t in V and e == EPSILON:
            desc = f"Expandir {t}"
        elif t in Sigma and e == t:
            desc = f"Match {t}"
        elif t == Z0 and e == EPSILON:
            desc = "Aceptacion"
        else:
            desc = ""
        print(f"  {i:3d} | {o:6s} | {e:8s} | {t:8s} | {d:7s} | {apilar:20s} | {desc}")

    trans_expansion = sum(1 for _, e, t, _, _ in delta if e == EPSILON and t in V)
    trans_match = sum(1 for _, e, t, _, _ in delta if e == t and t in Sigma)
    trans_epsilon = sum(1 for _, e, _, _, _ in delta if e == EPSILON)
    print(f"\nMetricas del PDA:")
    print(f"  | Metrica                           | Valor |")
    print(f"  |-----------------------------------|-------|")
    print(f"  | Estados totales                   | {len(Q):5d} |")
    print(f"  | Transiciones totales              | {len(delta):5d} |")
    print(f"  | Transiciones de expansion         | {trans_expansion:5d} |")
    print(f"  | Transiciones de matching          | {trans_match:5d} |")
    print(f"  | Transiciones epsilon              | {trans_epsilon:5d} |")
    print(f"  | Simbolos de pila                  | {len(Gamma):5d} |")


if __name__ == "__main__":
    from gramatica import compute_first, compute_follow
    first = compute_first()
    follow = compute_follow(first)

    mostrar_pda()

    print("\n" + "=" * 65)
    print("SIMULACION DEL PDA SOBRE CADENAS DE PRUEBA")
    print("=" * 65)
    from gramatica import CADENAS_EJEMPLO
    for c in CADENAS_EJEMPLO:
        aceptado, configs = simular_pda(c["tokens"])
        resultado = "ACEPTADO ✓" if aceptado else "RECHAZADO ✗"
        print(f"\n{c['id']}. {c['descripcion']}")
        print(f"   Entrada: {c['entrada']}")
        print(f"   Resultado: {resultado} (esperado: {'valida' if c['valida'] else 'invalida'})")
        print(f"   Configuraciones: {len(configs)}")
