"""
app.py - Frontend web para validar el analizador sintactico
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify
from parser import tokenizar, Parser, NodoAST, ErrorSintactico
from gramatica import metricas_gramatica, CADENAS_EJEMPLO, compute_first, compute_follow, check_ll1

app = Flask(__name__, 
            template_folder="../frontend/templates",
            static_folder="../frontend/static")


def nodo_a_dict(nodo):
    """Convierte NodoAST a diccionario para JSON."""
    if nodo is None:
        return None
    return {
        "tipo": nodo.tipo,
        "valor": nodo.valor,
        "hijos": [nodo_a_dict(h) for h in nodo.hijos] if nodo.hijos else []
    }


def arbol_a_texto(nodo, nivel=0):
    """Convierte el arbol a representacion textual."""
    if nodo is None:
        return ""
    indent = "  " * nivel
    if nodo.valor is not None:
        linea = f"{indent}{nodo.tipo}({nodo.valor})"
    else:
        linea = f"{indent}{nodo.tipo}"
    partes = [linea]
    for h in nodo.hijos:
        partes.append(arbol_a_texto(h, nivel + 1))
    return "\n".join(partes)


@app.route("/")
def index():
    """Pagina principal."""
    return render_template("index.html")


@app.route("/analizar", methods=["POST"])
def analizar():
    """Endpoint para analizar una entrada."""
    data = request.get_json()
    entrada = data.get("entrada", "").strip()

    if not entrada:
        return jsonify({"error": "Ingresa una cadena para analizar"}), 400

    try:
        tokens = tokenizar(entrada)
    except ValueError as e:
        return jsonify({
            "valida": False,
            "tokens": [],
            "error": str(e),
            "tipo_error": "lexico",
            "arbol": None,
            "arbol_texto": ""
        })

    try:
        parser = Parser(tokens)
        arbol = parser.parse()
        return jsonify({
            "valida": True,
            "tokens": tokens,
            "error": None,
            "tipo_error": None,
            "arbol": nodo_a_dict(arbol),
            "arbol_texto": arbol_a_texto(arbol),
            "total_tokens": len(tokens)
        })
    except ErrorSintactico as e:
        return jsonify({
            "valida": False,
            "tokens": tokens,
            "error": str(e),
            "tipo_error": "sintactico",
            "arbol": None,
            "arbol_texto": "",
            "pos_error": e.posicion,
            "esperado": str(e.esperado) if hasattr(e, 'esperado') else None,
            "encontrado": str(e.encontrado) if hasattr(e, 'encontrado') else None,
        })


@app.route("/metricas")
def metricas():
    """Endpoint con las metricas de la gramatica."""
    first = compute_first()
    follow = compute_follow(first)
    conflictos = check_ll1(first, follow)

    first_sets = {nt: sorted(list(f)) for nt, f in first.items() if nt in __import__('gramatica').V}
    follow_sets = {nt: sorted(list(f)) for nt, f in follow.items() if nt in __import__('gramatica').V}

    return jsonify({
        "no_terminales": len(__import__('gramatica').V),
        "terminales": len(__import__('gramatica').Sigma),
        "producciones": len(__import__('gramatica').P),
        "conflictos_ll1": len(conflictos),
        "es_ll1": len(conflictos) == 0,
        "cadenas_ejemplo": [
            {"id": c["id"], "descripcion": c["descripcion"], "entrada": c["entrada"]}
            for c in CADENAS_EJEMPLO
        ]
    })


@app.route("/cadenas_ejemplo")
def cadenas_ejemplo():
    """Devuelve las cadenas de ejemplo para el frontend."""
    return jsonify([
        {"id": c["id"], "descripcion": c["descripcion"], "entrada": c["entrada"]}
        for c in CADENAS_EJEMPLO
    ])


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
