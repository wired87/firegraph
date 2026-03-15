# Firegraph

Analyze Python code structure and build a relational graph of classes, methods, parameters, and their usage. Visualize the result as an interactive HTML graph.

## Workflow

1. **Input** — File path, folder path, or inline code string
2. **Parse** — AST traversal via `StructInspector` (classes, methods, params, class vars)
3. **Link** — `UsageLinker` adds METHOD→METHOD (calls) and PARAM→METHOD (passes_to)
4. **Folder mapping** — If path is a folder: `os.walk` adds FOLDER nodes and `contains` edges
5. **Output** — `output/graph.json` (NetworkX) and `output/graph.html` (pyvis interactive viz)

## Setup

```bash
pip install -r r.txt
```

Dependencies: `networkx`, `pyvis`

## Tutorial

### 1. Analyze the project (default)

Run with no arguments to analyze the project directory:

```bash
python main.py
```

### 2. Analyze a single file

```bash
python main.py graph_creator.py
```

### 3. Analyze a folder

```bash
python main.py .
python main.py path/to/package
```

### 4. Analyze inline code

```bash
python main.py --text "def foo(x): return bar(x)"
```

### 5. Custom output directory

```bash
python main.py -o my_output
python main.py graph_creator.py -o results
```

### 6. View the result

Open `output/graph.html` in a browser. The graph shows:

- **MODULE** — Python modules
- **CLASS** — Classes
- **METHOD** — Functions and methods
- **PARAM** — Parameters and return values
- **FOLDER** — Directories (when analyzing a folder)

Edges indicate relationships (e.g. `has_method`, `calls`, `contains`).

## Edge Types

| rel            | src      | trgt      | Meaning                 |
|----------------|----------|-----------|-------------------------|
| has_class      | MODULE   | CLASS     | Module contains class   |
| has_method     | MODULE   | METHOD    | Module contains method  |
| has_method     | CLASS    | METHOD    | Class contains method   |
| has_var        | CLASS    | CLASS_VAR | Class contains variable |
| requires_param | METHOD   | PARAM     | Method requires param   |
| returns_param  | METHOD   | PARAM     | Method returns param    |
| calls          | METHOD   | METHOD    | Method calls another    |
| passes_to      | PARAM    | METHOD    | Param passed to method  |
| contains       | FOLDER   | FOLDER    | Dir contains subdir     |
| contains       | FOLDER   | MODULE    | Dir contains module     |

## Project Layout

```
firegraph/
├── main.py          # Entry point
├── run_firegraph.py # Workflow + validation
├── graph_creator.py # StructInspector, UsageLinker
├── graph/
│   └── visual.py    # Pyvis visualization
├── r.txt            # Requirements
└── output/
    ├── graph.json   # Serialized graph
    └── graph.html   # Interactive visualization
```

## Programmatic Use

```python
from run_firegraph import run_workflow

# Analyze a folder
G, json_path, html_path = run_workflow("path/to/project", is_path=True)

# Analyze inline code
G, json_path, html_path = run_workflow("def foo(): pass", is_path=False)
```
