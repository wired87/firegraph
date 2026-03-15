# Firegraph

Analyze Python code structure and build a relational graph of classes, methods, parameters, and their usage. Visualize the result as an interactive HTML graph.

## Workflow

1. **Input** — File path, folder path, or inline code string
2. **Parse** — AST traversal via `StructInspector` (classes, methods, params, class vars)
3. **Link** — `UsageLinker` adds METHOD→METHOD (calls) and PARAM→METHOD (passes_to)
4. **Folder mapping** — If path is a folder: `os.walk` adds FOLDER nodes and `contains` edges
5. **SemanticMaster** (optional) — Adds 24 TECHNIQUE nodes, embeds all nodes, creates similarity edges
6. **Output** — `output/graph.json` (NetworkX) and `output/graph.html` (pyvis interactive viz)

## Setup

```bash
pip install -r r.txt
```

Dependencies: `networkx`, `pyvis`. For SemanticMaster: `embedder` (sentence_transformers).

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
- **TECHNIQUE** — Data-science techniques (when using SemanticMaster)

Edges indicate relationships (e.g. `has_method`, `calls`, `contains`, `CosineSimilarity`, technique names).

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
| CosineSimilarity | NODE   | NODE      | Semantic similarity (SemanticMaster) |
| *technique*    | NODE     | TECHNIQUE | Code matches technique (SemanticMaster) |

## Project Layout

```
firegraph/
├── main.py              # Entry point
├── run_firegraph.py     # Workflow + validation
├── graph_creator.py     # StructInspector, UsageLinker
├── embedder/            # Embeddings (sentence_transformers)
├── graph/
│   ├── visual.py        # Pyvis visualization
│   ├── semantic_master.py  # SemanticMaster, DATA_PROCESSORS
│   └── local_graph_utils.py
├── r.txt                # Requirements
└── output/
    ├── graph.json       # Serialized graph
    └── graph.html       # Interactive visualization
```

## SemanticMaster

SemanticMaster enriches the code graph with **24 data-science technique nodes** and **semantic similarity edges**. It embeds all nodes (using `sentence_transformers` via the `embedder` package), then links:

- **Node ↔ Node** — `CosineSimilarity` edges when embeddings are similar
- **Node ↔ TECHNIQUE** — edges when code/params match a technique (rel = technique name)

### Capabilities

| Capability | Description |
|------------|--------------|
| **Embed all nodes** | Converts node id, type, name, docstring, equation, code into text and embeds via sentence-transformers |
| **Technique nodes** | Adds 24 TECHNIQUE nodes with equation + Python library metadata |
| **Similarity edges** | Creates edges above a configurable threshold (default 0.5) |
| **Multi-rel edges** | Edge `rel` varies per technique for color-coded visualization |

### Data Processing Techniques (24)

| Technique | Equation | Python Libraries |
|-----------|----------|------------------|
| GradientDescent | θ_{j+1} = θ_j − α·∇J(θ_j) | torch.optim.SGD, jax, scipy.optimize |
| NormalDistribution | f(x\|μ,σ²) = (1/(σ√2π))·exp(−(x−μ)²/(2σ²)) | scipy.stats.norm, numpy.random.normal, torch.distributions |
| ZScore | z = (x − μ) / σ | scipy.stats.zscore, sklearn.StandardScaler |
| Sigmoid | σ(x) = 1/(1 + e^{-x}) | torch.nn.Sigmoid, scipy.special.expit, jax.nn.sigmoid |
| Correlation | corr(X,Y) = Cov(X,Y)/(Std(X)·Std(Y)) | numpy.corrcoef, scipy.stats.pearsonr, pandas.corr |
| CosineSimilarity | (A·B)/(‖A‖·‖B‖) | sklearn.cosine_similarity, scipy.spatial.distance |
| NaiveBayes | P(y\|x₁..xₙ) ∝ P(y)·Π P(xᵢ\|y) | sklearn.naive_bayes.GaussianNB, MultinomialNB |
| MaximumLikelihoodEstimation | argmax_θ Π P(xᵢ\|θ) | scipy.optimize, statsmodels |
| OrdinaryLeastSquares | β = (XᵀX)^{-1} Xᵀy | sklearn.LinearRegression, statsmodels.OLS, np.linalg.lstsq |
| F1Score | F1 = 2·Precision·Recall/(Precision+Recall) | sklearn.metrics.f1_score |
| ReLU | ReLU(x) = max(0,x) | torch.nn.ReLU, jax.nn.relu |
| EigenVectors | Av = λv | numpy.linalg.eig, scipy.linalg.eig |
| R2Score | R² = 1 − Σ(yᵢ−ŷ)²/Σ(yᵢ−ȳ)² | sklearn.metrics.r2_score |
| Softmax | softmax(xᵢ) = exp(xᵢ)/Σ exp(xⱼ) | torch.nn.Softmax, jax.nn.softmax, scipy.special.softmax |
| MeanSquaredError | MSE = (1/n) Σ(yᵢ−ŷ)² | sklearn.metrics.mean_squared_error, torch.nn.MSELoss |
| RidgeRegression | MSE + λ Σ βⱼ² | sklearn.linear_model.Ridge |
| Entropy | H(P) = −Σ P(x) log P(x) | scipy.stats.entropy |
| KLDivergence | D_KL(P‖Q) = Σ P(x) log(P(x)/Q(x)) | scipy.stats.entropy, torch.nn.functional.kl_div |
| LogLoss | −(1/N) Σ [y log p + (1−y) log(1−p)] | sklearn.metrics.log_loss, torch.nn.BCELoss |
| SVD | A = U Σ Vᵀ | numpy.linalg.svd, scipy.linalg.svd, torch.linalg.svd |
| LagrangeMultiplier | L(x,λ) = f(x) − λg(x) | scipy.optimize.minimize(method='SLSQP') |
| SVM | min ½‖w‖² + C Σ max(0, 1−yᵢ(w·xᵢ−b)) | sklearn.svm.SVC, LinearSVC |
| LinearRegression | y = β₀ + β₁x₁ + … + βₙxₙ + ε | sklearn.linear_model.LinearRegression |
| PCA | X_reduced = X @ Vₖ (V from SVD) | sklearn.decomposition.PCA, numpy.linalg.svd |

### Possible Applications

- **Code–technique mapping** — Discover which code (classes, methods) aligns with known ML/statistics techniques
- **Refactoring hints** — Find semantically similar modules for consolidation or deduplication
- **Documentation** — Auto-suggest technique labels for undocumented functions
- **Onboarding** — Visualize how project components relate to standard data-science concepts
- **Tech debt** — Identify orphaned or duplicate logic via similarity clusters
- **Library migration** — Map custom implementations to canonical libraries (e.g. sklearn, torch)

### Usage

```python
from run_firegraph import run_workflow
from graph import SemanticMaster, GUtils

G, json_path, html_path = run_workflow("path/to/project", is_path=True)
g_utils = GUtils(G)
sm = SemanticMaster(g_utils)
sm.run(threshold=0.5)  # add techniques + similarity edges
# Re-save graph / re-render HTML with enriched graph
```

Requires `embedder` (sentence_transformers). If unavailable, SemanticMaster is disabled and a warning is printed to stderr.

---

## Programmatic Use

```python
from run_firegraph import run_workflow

# Analyze a folder
G, json_path, html_path = run_workflow("path/to/project", is_path=True)

# Analyze inline code
G, json_path, html_path = run_workflow("def foo(): pass", is_path=False)
```
