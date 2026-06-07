# Análisis de Resultados

Los hallazgos y productos obtenidos en este proyecto se estructuran en correspondencia directa con los objetivos específicos planteados, dividiéndose en el modelado formal de la gramática, la especificación matemática del autómata de pila y la arquitectura del analizador implementado.

---

## 9.1 Modelo Formal de la Gramática Libre de Contexto (GLC)

Se definió matemáticamente la gramática para el reconocimiento de las estructuras de control mediante la cuádrupla formal:

$$G = (V, \Sigma, P, S)$$

### Símbolos No Terminales ($V$)

$$
\begin{aligned}
V = \{ & \text{Program, Stmt, IfStmt, WhileStmt, AssignStmt, Block,} \\
       & \text{StmtList, RestStmtList, Cond, RelOp, Expr, ExprPrime,} \\
       & \text{AddOp, Term, TermPrime, MulOp, Factor} \}
\end{aligned}
$$

Total: **17** símbolos no terminales.

### Símbolos Terminales ($\Sigma$)

$$
\Sigma = \{\text{'if', 'then', 'else', 'while', 'do', 'true', 'false', 'id', 'num', }\newline
\text{'=' , '==', '<', '>', '(', ')', '\{', '\}', ';', '+', '-', '*', '/'}\}
$$

Total: **22** símbolos terminales.

### Símbolo Inicial ($S$)

$$S = \text{Program}$$

### Reglas de Producción ($P$)

Las reglas se factorizaron rigurosamente para eliminar la recursividad a la izquierda y la ambigüedad, quedando estructuradas de la siguiente manera:

$$
\begin{array}{rcll}
(1) & \text{Program} & \rightarrow & \text{Stmt} \\[4pt]
(2) & \text{Stmt} & \rightarrow & \text{IfStmt} \\
(3) & & | & \text{WhileStmt} \\
(4) & & | & \text{AssignStmt} \\
(5) & & | & \text{Block} \\[4pt]
(6) & \text{IfStmt} & \rightarrow & \text{'if' Cond 'then' Stmt 'else' Stmt} \\[4pt]
(7) & \text{WhileStmt} & \rightarrow & \text{'while' Cond 'do' Stmt} \\[4pt]
(8) & \text{Block} & \rightarrow & \text{'\{' StmtList '\}'} \\[4pt]
(9) & \text{StmtList} & \rightarrow & \text{Stmt RestStmtList} \\[4pt]
(10) & \text{RestStmtList} & \rightarrow & \text{';' Stmt RestStmtList} \\
(11) & & | & \epsilon \\[4pt]
(12) & \text{AssignStmt} & \rightarrow & \text{'id' '=' Expr} \\[4pt]
(13) & \text{Cond} & \rightarrow & \text{Expr RelOp Expr} \\
(14) & & | & \text{'true'} \\
(15) & & | & \text{'false'} \\[4pt]
(16) & \text{RelOp} & \rightarrow & \text{'=='} \\
(17) & & | & \text{'<'} \\
(18) & & | & \text{'>'} \\[4pt]
(19) & \text{Expr} & \rightarrow & \text{Term ExprPrime} \\[4pt]
(20) & \text{ExprPrime} & \rightarrow & \text{AddOp Term ExprPrime} \\
(21) & & | & \epsilon \\[4pt]
(22) & \text{AddOp} & \rightarrow & \text{'+'} \\
(23) & & | & \text{'-'} \\[4pt]
(24) & \text{Term} & \rightarrow & \text{Factor TermPrime} \\[4pt]
(25) & \text{TermPrime} & \rightarrow & \text{MulOp Factor TermPrime} \\
(26) & & | & \epsilon \\[4pt]
(27) & \text{MulOp} & \rightarrow & \text{'*'} \\
(28) & & | & \text{'/'} \\[4pt]
(29) & \text{Factor} & \rightarrow & \text{'id'} \\
(30) & & | & \text{'num'} \\
(31) & & | & \text{'(' Expr ')'}
\end{array}
$$

Total: **31** producciones, de las cuales **3** son producciones epsilon ($\epsilon$).

### Verificación de No Ambigüedad

Para validar que cada cadena admite un único árbol de derivación (evitando la ambigüedad clásica del *"dangling else"*), se analizó la derivación formal de 5 cadenas representativas.

#### Estrategia contra el *dangling else*

La gramática definida exige que todo `if` tenga su correspondiente `else`, eliminando la producción `IfStmt → 'if' Cond 'then' Stmt`. Esto impide que el parser genere dos interpretaciones estructurales distintas para una misma secuencia de entrada, pues no existe la forma sin `else` que pudiera asociarse ambiguamente.

#### Cadenas analizadas

| # | Descripción | Tokens | Árbol único |
|---|---|---|---|
| 1 | `if (x==1) then y=0 else z=1` | 12 | Sí ✓ |
| 2 | `while (x>0) do x=x-1` | 10 | Sí ✓ |
| 3 | `if (x==1) then if (y==2) then a=1 else a=2 else b=1` | 19 | Sí ✓ |
| 4 | `while (x>0) do { s=s+x ; x=x-1 }` | 18 | Sí ✓ |
| 5 | `if (x==1) then while (y>0) do y=y-1 else x=0` | 16 | Sí ✓ |

**Resultado:** Las 5 cadenas producen un único árbol de derivación. La gramática es **no ambigua** para el conjunto evaluado.

### Verificación LL(1)

Mediante el cómputo de los conjuntos FIRST y FOLLOW, se verificó que la gramática pertenece a la clase LL(1), es decir, puede ser analizada con un *lookahead* de un token sin conflictos:

| Métrica | Valor |
|---|---|
| No terminales | 17 |
| Terminales | 22 |
| Producciones | 31 |
| Producciones $\epsilon$ | 3 |
| No terminales anulables | 3 |
| **Conflictos FIRST-FIRST** | **0** |
| **Conflictos FIRST-FOLLOW** | **0** |
| **Conclusión** | **Gramática LL(1)** ✓ |

---

## 9.2 Especificación Formal del Autómata de Pila (PDA)

Para fundamentar el comportamiento del analizador, se modeló un Autómata con Pila que reconoce el lenguaje por pila vacía y estado final, definido por la séptima tupla:

$$M = (Q, \Sigma, \Gamma, \delta, q_0, Z_0, F)$$

### Componentes del autómata

**Estados ($Q$):** 3 estados

$$Q = \{q_0, q_1, q_f\}$$

donde $q_0$ es el estado inicial, $q_1$ es el estado de trabajo y $q_f$ es el estado final de aceptación.

**Alfabeto de Entrada ($\Sigma$):** El mismo alfabeto de terminales de la GLC: 22 símbolos.

**Alfabeto de Pila ($\Gamma$):** Compuesto por los no terminales, los terminales y el marcador de fondo:

$$\Gamma = V \cup \Sigma \cup \{Z_0\}$$

Total: **40** símbolos en el alfabeto de pila.

**Estado Inicial ($q_0$):** $q_0$

**Símbolo Inicial de Pila ($Z_0$):** $Z_0$ (marcador de fondo)

**Estados Finales ($F$):** $F = \{q_f\}$

### Funciones de Transición ($\delta$)

Las transiciones se clasifican en cuatro categorías:

#### 1. Transición de inicio (1 transición)

$$\delta(q_0, \epsilon, \epsilon) = \{(q_1, S \cdot Z_0)\}$$

Apila el símbolo inicial $S$ (Program) sobre el marcador de fondo $Z_0$.

#### 2. Transiciones de expansión sintáctica (31 transiciones)

Mapean directamente las producciones de la gramática. Cada producción $A \rightarrow \alpha$ genera:

$$\delta(q_1, \epsilon, A) = \{(q_1, \alpha)\}$$

Por ejemplo, para las producciones de control de flujo:

$$
\begin{aligned}
\delta(q_1, \epsilon, \text{IfStmt}) &= \{(q_1, \text{'if'} \cdot \text{Cond} \cdot \text{'then'} \cdot \text{Stmt} \cdot \text{'else'} \cdot \text{Stmt})\} \\
\delta(q_1, \epsilon, \text{WhileStmt}) &= \{(q_1, \text{'while'} \cdot \text{Cond} \cdot \text{'do'} \cdot \text{Stmt})\} \\
\delta(q_1, \epsilon, \text{Block}) &= \{(q_1, \text{'\{} \cdot \text{StmtList} \cdot \text{'\}'})\}
\end{aligned}
$$

Para las producciones epsilon (RestStmtList, ExprPrime, TermPrime):

$$\delta(q_1, \epsilon, A) = \{(q_1, \epsilon)\}$$

que desapila el no terminal sin apilar ningún símbolo nuevo.

#### 3. Transiciones de consumo o *matching* (22 transiciones)

Para cada terminal $a \in \Sigma$:

$$\delta(q_1, a, a) = \{(q_1, \epsilon)\}$$

Validación del balanceo de delimitadores:

$$
\begin{aligned}
\delta(q_1, \text{'\{}', \text{'\{}'}) &= \{(q_1, \epsilon)\} \\
\delta(q_1, \text{'\}'}, \text{'\}'}\}) &= \{(q_1, \epsilon)\} \\
\delta(q_1, \text{'('}, \text{'('}) &= \{(q_1, \epsilon)\} \\
\delta(q_1, \text{')'}, \text{')'}) &= \{(q_1, \epsilon)\}
\end{aligned}
$$

#### 4. Transición de aceptación (1 transición)

$$\delta(q_1, \epsilon, Z_0) = \{(q_f, \epsilon)\}$$

Cuando la pila se reduce únicamente al marcador $Z_0$ sin más entrada, el autómata transita al estado final $q_f$, indicando que la cadena ha sido aceptada.

### Resumen de transiciones

| Tipo | Cantidad | Descripción |
|---|---|---|
| Inicio | 1 | $q_0 \rightarrow q_1$, apilar $S Z_0$ |
| Expansión | 31 | Una por producción ($\epsilon$, no terminal) |
| Matching | 22 | Una por terminal ($a$, $a$) |
| Aceptación | 1 | $Z_0$ en pila, $\epsilon$ en entrada |
| **Total** | **55** | |

### Simulación del PDA

El autómata fue simulado sobre las 5 cadenas de prueba, obteniendo los siguientes resultados:

| # | Descripción | Tokens | Transiciones ejecutadas | Resultado |
|---|---|---|---|---|
| 1 | IF-ELSE simple | 12 | 43 | Aceptado ✓ |
| 2 | WHILE simple | 10 | 39 | Aceptado ✓ |
| 3 | IF-ELSE anidado | 19 | 73 | Aceptado ✓ |
| 4 | WHILE con bloque | 18 | 64 | Aceptado ✓ |
| 5 | IF con WHILE anidado | 16 | 69 | Aceptado ✓ |

Todas las cadenas válidas son aceptadas por el PDA, confirmando que el autómata reconoce exactamente el lenguaje generado por la gramática.

---

## 9.3 Resultados de la Implementación del Parser en Python

La traducción de los modelos formales a software dio como resultado un programa modular estructurado bajo el paradigma orientado a objetos, compuesto por 457 líneas de código distribuidas en tres módulos.

### Arquitectura del sistema

```
Entrada (string)
     │
     ▼
┌─────────────┐
│ tokenizar() │  →  Lista de tokens
└─────────────┘
     │
     ▼
┌─────────────────────────────────┐
│ Parser (descenso recursivo)     │
│  ├── parse_Program()            │
│  ├── parse_Stmt()               │
│  ├── parse_IfStmt()             │
│  ├── parse_WhileStmt()          │
│  ├── parse_Block()              │
│  ├── parse_StmtList()           │
│  ├── parse_RestStmtList()       │
│  ├── parse_AssignStmt()         │
│  ├── parse_Cond()               │
│  ├── parse_RelOp()              │
│  ├── parse_Expr()               │
│  ├── parse_ExprPrime()          │
│  ├── parse_AddOp()              │
│  ├── parse_Term()               │
│  ├── parse_TermPrime()          │
│  ├── parse_MulOp()              │
│  └── parse_Factor()             │
└─────────────────────────────────┘
     │
     ├── Éxito → NodoAST (árbol de derivación)
     └── Error → ErrorSintactico (tipo + posición + token esperado)
```

### Mapeo de funciones modulares

Cada símbolo no terminal del modelo formal se implementó como un método de clase independiente dentro de la clase `Parser`. La correspondencia es biunívoca:

| No terminal | Método | Producciones |
|---|---|---|
| Program | `parse_Program()` | 1 |
| Stmt | `parse_Stmt()` | 4 (selección por *lookahead*) |
| IfStmt | `parse_IfStmt()` | 1 |
| WhileStmt | `parse_WhileStmt()` | 1 |
| Block | `parse_Block()` | 1 |
| StmtList | `parse_StmtList()` | 1 |
| RestStmtList | `parse_RestStmtList()` | 2 (con predicción $\epsilon$) |
| AssignStmt | `parse_AssignStmt()` | 1 |
| Cond | `parse_Cond()` | 3 (selección por *lookahead*) |
| RelOp | `parse_RelOp()` | 3 |
| Expr | `parse_Expr()` | 1 |
| ExprPrime | `parse_ExprPrime()` | 2 (con predicción $\epsilon$) |
| AddOp | `parse_AddOp()` | 2 |
| Term | `parse_Term()` | 1 |
| TermPrime | `parse_TermPrime()` | 2 (con predicción $\epsilon$) |
| MulOp | `parse_MulOp()` | 2 |
| Factor | `parse_Factor()` | 3 (selección por *lookahead*) |

La recursividad inherente de la gramática es manejada directamente por la pila de llamadas nativa de Python, que mantiene el contexto de anidamiento sin necesidad de una pila explícita.

### Construcción dinámica del árbol

A medida que el flujo de ejecución avanza de manera descendente, los métodos retornan instancias de la clase `NodoAST`, que encapsulan:

- **tipo**: nombre del no terminal o terminal
- **valor**: contenido semántico (cuando aplica, ej. literales)
- **hijos**: lista de subárboles (estructura jerárquica anidada)

Ejemplo del árbol generado para `while x > 0 do { s = s + x ; x = x - 1 }`:

```
Program
 └── WhileStmt
      ├── Cond
      │    ├── Expr → Term → Factor → id
      │    ├── RelOp → >
      │    └── Expr → Term → Factor → num
      └── Block
           └── StmtList
                ├── AssignStmt
                │    ├── id
                │    ├── =
                │    └── Expr → Term → Factor → id
                │         └── ExprPrime → AddOp(+) → Term → Factor → id
                │              └── ExprPrime → ε
                └── RestStmtList
                     ├── ;
                     ├── AssignStmt → id = Expr → Term → Factor → id
                     │    └── ExprPrime → AddOp(-) → Term → Factor → num
                     │         └── ExprPrime → ε
                     └── RestStmtList → ε
```

Si la cadena es válida, el sistema entrega un árbol de derivación completo que refleja la jerarquía exacta del código fuente analizado.

### Manejo y tipificación de errores sintácticos

El parser no se limita a un diagnóstico binario (válido/inválido), sino que integra un control de excepciones avanzado capaz de discriminar y reportar la naturaleza exacta de la falla mediante la excepción `ErrorSintactico`.

#### Escenarios de error capturados

| Tipo de error | Descripción | Ejemplo de entrada |
|---|---|---|
| **Token inesperado** | El token actual no coincide con el esperado por la regla gramatical | `if x == 1 then y = 0` (falta `else`) |
| **Fin de entrada prematuro** | La secuencia de tokens termina antes de completar las producciones obligatorias | `{ x = 1 ; y = 2` (falta `}`) |
| **Token inválido en contexto** | El token no pertenece al conjunto válido para la posición actual | `if x == then y = 1` (`then` como expresión) |
| **Error léxico** | Caracter no reconocido por el tokenizador | `if @x == 1 then y = 0` |

### Resultados de las pruebas

Se ejecutó una suite de **18 casos de prueba** distribuidos en 10 válidos y 8 inválidos:

| Tipo | Casos | Aciertos | Porcentaje |
|---|---|---|---|
| Cadenas válidas | 10 | 10 | 100% |
| Cadenas inválidas | 8 | 8 | 100% |
| **Total** | **18** | **18** | **100%** |

El sistema clasificó correctamente la totalidad de las cadenas, demostrando que la implementación del parser corresponde fielmente a la gramática formal definida.

### Estructura de archivos

```
analizador-sintactico/
├── gramatica.py    (311 líneas)  — Definición G=(V,Σ,P,S), FIRST, FOLLOW, LL(1)
├── pda.py          (178 líneas)  — PDA M=(Q,Σ,Γ,δ,q₀,Z₀,F) + simulación
├── parser.py       (457 líneas)  — Parser descendente recursivo + árbol + pruebas
└── resultados.md   (517 líneas)  — Documento de resultados
```
