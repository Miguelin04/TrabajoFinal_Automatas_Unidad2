# Proyecto Final - Autómatas Unidad 2

Este proyecto implementa un analizador sintáctico y una interfaz web para validar gramáticas. 

## Estructura del Proyecto

El proyecto está organizado en las siguientes carpetas:

- `backend/`: Contiene la lógica del servidor y los algoritmos (Flask, parser, gramática, PDA).
- `frontend/`: Contiene los recursos visuales y las plantillas web (HTML, CSS, JS).

## Requisitos

- Python 3.x
- Flask

Puedes instalar Flask con:

```bash
pip install Flask
```

## Cómo ejecutar

1. Abre una terminal y navega a la carpeta `backend`:
   ```bash
   cd backend
   ```

2. Ejecuta la aplicación Flask:
   ```bash
   python app.py
   ```

3. Abre tu navegador y dirígete a `http://localhost:5000`.

## Componentes

- `backend/app.py`: Archivo principal del servidor Flask.
- `backend/gramatica.py`: Lógica para el cálculo de los conjuntos FIRST, FOLLOW y validación LL(1).
- `backend/parser.py`: Implementación del analizador sintáctico (Parser) y construcción del AST.
- `backend/pda.py`: Autómata con Pila.
- `frontend/templates/`: Vistas HTML.
- `frontend/static/`: Archivos estáticos como estilos CSS y scripts de JavaScript.
