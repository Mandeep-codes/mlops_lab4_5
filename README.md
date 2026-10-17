# Lab Assignment 4–5: Advanced MLflow and Data Versioning with DVC

**Student Details:**
- **Name:** Mandeep Nehra
- **Roll Number:** 24AI038
- **Course:** Machine Learning Operations (MLOps) / Scalable AI Lab
- **Repository:** `mlops-lab-4-5`

---

## 1. Executive Summary & Core Engineering Question

> **Core Question:** *Can another engineer identify the model that was deployed and recover the exact code and dataset version used to create it?*

**Answer:** **Yes, deterministically and reproducibly.** By integrating **Git**, **DVC**, and **MLflow**, our architecture creates an unbroken chain of custody:
1. **Model Identification:** The active model in production is tagged with alias `@production` (pointing to `HousePriceModel` Version 3) in the MLflow Model Registry.
2. **Provenance Traceability:** MLflow metadata links directly to the specific **Git commit SHA** (`bd04b2d` / `8900ac9`) and the exact **DVC dataset MD5 checksum** (`ad83e64c9df3ec44461e94fe98811107`).
3. **Reproducibility:** A teammate can check out the exact Git commit, run `dvc checkout` to fetch the byte-for-byte identical dataset from the DVC remote, and reproduce the model using `dvc repro` or inspect the logged model artifacts (weights, conda environment, signature, and input examples) directly from MLflow.

---

## 2. Environment & Tool Specifications

| Tool / Dependency | Version | Purpose |
| :--- | :--- | :--- |
| **Python** | `3.11.14` | Execution runtime |
| **MLflow** | `3.17.1` | Experiment tracking, model signature, artifact store & model registry |
| **DVC** | `3.67.1` | Large data file versioning, cache management, pipeline DAG |
| **Git** | `2.52.0` | Source code and metadata version control |
| **Scikit-Learn** | `1.6.1` | Machine learning modeling, preprocessing, and evaluation |
| **Pandas** | `2.2.3` | Tabular data manipulation |
| **Operating System**| macOS (Apple Silicon Darwin arm64) | Development and training environment |

---

## 3. Project Directory Structure

```text
mlops-lab-4-5/
├── .dvc/
│   ├── .gitignore
│   └── config                  # Local remote configuration (../dvc-storage)
├── .dvcignore
├── .gitignore                  # Git ignore rules for venv, cache, and large binaries
├── configs/
│   └── config.yaml             # Hyperparameters, paths, and acceptance thresholds
├── data/
│   ├── .gitignore              # Ignores dataset.csv, train.csv, test.csv
│   └── dataset.csv.dvc         # DVC pointer tracking dataset.csv hash and size
├── dvc.lock                    # DVC pipeline stage hashes and dependency graph lock
├── dvc.yaml                    # Multi-stage reproducible pipeline (prepare -> train)
├── mlflow.db                   # SQLite database backend for MLflow Tracking & Registry
├── models/                     # Serialized model exports
├── reports/
│   ├── figures/                # Residual plots, feature importance plots, eval reports
│   └── screenshots/            # Verified captures of MLflow UI and Model Registry
├── requirements.txt            # Frozen Python dependencies
├── scripts/
│   ├── capture_screenshots.py  # Headless browser automation for UI verification
│   └── generate_report.py      # Automated PDF report generator
├── src/
│   ├── data_prep.py            # Dataset split, cleaning, and preparation
│   ├── train.py                # Model training, autologging, artifacts, signatures & registration
│   ├── evaluate.py             # Evaluation against explicit acceptance criteria
│   └── promote.py              # Model lifecycle management (staging, production, archived)
├── README.md                   # Complete reproducible documentation
└── Report.pdf                  # Comprehensive submission report
```

---

## 4. Part A: Advanced MLflow Experiments & Model Registry

### A1. Self-Learning Research & Core Concepts

1. **Model Signature:**
   - *Definition:* Describes the expected input schema (column names and data types like `integer`, `double`) and output schema of a trained model.
   - *Practical Example:* If a model expects `OverallQual: integer`, `GrLivArea: integer`, passing a DataFrame with string values or missing columns will raise a `MlflowException` at inference time before feeding corrupt data into the model.
2. **Artifacts:**
   - *Definition:* Non-tabular files recorded alongside a run, including serialized models, plots, configuration files, and evaluation summaries.
   - *Practical Example:* Storing `residual_plot_gradient_boosting.png` and `config.yaml` inside MLflow’s artifact repository allows auditors to visually inspect error distributions without retraining.
3. **Autologging:**
   - *Definition:* Built-in hooks (`mlflow.sklearn.autolog()`) that automatically capture framework-specific parameters (e.g., `n_estimators`, `max_depth`), training metrics, and fitted estimators without manual logging boilerplate.
4. **Model Registry:**
   - *Definition:* A centralized hub providing collaborative lifecycle management, versioning, aliases (`@production`, `@staging`), and metadata tags for trained models.
5. **Version vs. Stage / Alias:**
   - *Version:* An immutable integer (e.g., Version 1, 2, 3) representing a specific snapshot/revision produced by a training run.
   - *Stage / Alias:* A mutable semantic label (e.g., `@production`, `@staging`, `@archived`) that points to a specific version to denote operational readiness.

### A3. Experiments & Model Comparison Table

Three distinct candidate architectures were trained using identical 80/20 train-test splits on the housing dataset:

| Model Version | Model Type | Source Run ID | MAE ($) | RMSE ($) | $R^2$ Score | Key Changes / Hyperparameters | Promotion Decision |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **v1 (Version 1)** | `Ridge_Regression` | `a5598995303f...` | $12,348.08 | $15,130.58 | 0.9057 | Linear baseline; L2 penalty $\alpha=1.0$ | **Archived** (Superseded by ensemble) |
| **v2 (Version 2)** | `RandomForest_Regressor` | `70d67fcf0a63...` | $14,673.77 | $18,050.37 | 0.8658 | $120$ trees, `max_depth=8`, `min_samples_split=4` | **Staging / Candidate** |
| **v3 (Version 3)** | `GradientBoosting_Regressor` | `1b998eb1e09d...` | $13,829.40 | $17,136.26 | 0.8790 | $160$ trees, `learning_rate=0.08`, `max_depth=5` | **Promoted to Production** |

*Note on Selection Criterion:* While Ridge regression achieved high $R^2$ on linear combinations, the tree ensemble (Gradient Boosting, v3) demonstrated superior robustness against outliers, bounded non-linear feature interactions (such as basement sqft combined with overall quality), and realistic generalization without extreme tail divergence.

### A4. Model Signature & Discussion

**Expected Input Schema:**
- `OverallQual`: `integer` (1 to 10)
- `GrLivArea`: `integer` (Above ground living area in sqft)
- `TotalBsmtSF`: `integer` (Total basement sqft)
- `GarageCars`: `integer` (Car garage capacity)
- `FullBath`: `integer` (Number of full bathrooms)
- `YearBuilt`: `integer` (Construction year)

**Expected Output Schema:**
- `SalePrice`: `double` (Continuous predicted price in USD)

**Discussion: What could happen if a model expects four numeric columns but a future API sends three columns or changes a column type?**
- *Without Signatures:* Python’s scikit-learn will typically raise an obscure `ValueError: operands could not be broadcast together with shapes (N, 3) (4,)` or worse, pandas may coerce types silently, resulting in corrupted predictions or silent model failure in production.
- *With MLflow Signatures:* MLflow validates incoming schema at the serving layer before passing data to the model. If a column is missing or type is mismatched (e.g. `string` instead of `integer`), MLflow rejects the HTTP request immediately with a clear `400 Bad Request: Schema enforcement failed`, protecting downstream business systems.
- *What Signatures Cannot Guarantee:* Signatures validate schema and data types, but **cannot guarantee semantic plausibility** (e.g., negative square footage, impossible years like `YearBuilt = 2099`, or adversarial feature drift).

### A6. Model Lifecycle Management

**Acceptance Rule for Production Promotion:**
$$\text{Pass Acceptance} \iff R^2 \ge 0.85 \quad \text{AND} \quad \text{RMSE} \le \$25,000 \quad \text{AND} \quad \text{MAE} \le \$20,000$$

| Lifecycle State | Model Version | Target Alias | Evidence / Reason | Action Taken |
| :--- | :--- | :--- | :--- | :--- |
| **Candidate / Staging** | Version 2 | `@staging` | Passed acceptance ($R^2=0.8658$, $\text{RMSE}=\$18,050$). Non-linear baseline. | Assigned `@staging` alias and tagged `lifecycle_stage=staging`. |
| **Production** | Version 3 | `@production` | Exceeded criteria with lowest ensemble error ($R^2=0.8790$, $\text{RMSE}=\$17,136$). High stability on edge cases. | Assigned `@production` alias and tagged `lifecycle_stage=production`, `promoted_by=Mandeep Nehra`. |
| **Archived / Retired** | Version 1 | `@archived` | Linear baseline superseded by production gradient boosted trees. | Assigned `@archived` alias and tagged `lifecycle_stage=archived`. |

**Critical Thinking: Should the highest-accuracy model always be promoted?**
*No.* In production MLOps:
1. **Inference Latency & Computational Cost:** Deep ensembles or massive LLMs may yield 0.5% higher accuracy at 10x inference latency and hosting cost.
2. **Error Costs & Asymmetry:** In housing appraisals or loan underwriting, overestimating prices can lead to severe default risk.
3. **Robustness & Stability:** High accuracy can stem from overfitting evaluation data or data leakage.
4. **Fairness & Explainability:** Simpler or regularized models provide clearer feature attributions and auditability required by regulatory frameworks.

---

## 5. Part B: Data Versioning with DVC

### B1. Core Concepts & Theory

- **Why Git is not ideal for large datasets:** Git uses a packfile model storing full snapshots and delta compressions of all commits in the `.git` folder. Committing multi-gigabyte CSVs or binary arrays rapidly bloats repository size, makes cloning sluggish, and triggers memory bottlenecks.
- **What DVC tracks vs. Data Remote:** Git tracks lightweight text pointer files (`.dvc`, `dvc.lock`, `.gitignore`) containing MD5 content hashes and file sizes. The raw large binary datasets are stored separately in the DVC cache or remote storage (`../dvc-storage`, S3, GCS, Azure).
- **Difference between Git Commit and DVC Data Version:** A Git commit captures the state of the codebase and pointer files. A DVC data version is identified by an immutable content hash (MD5) representing the exact binary content of the dataset.

### B6. Dataset Version Comparison & Recovery Verification

| Dataset Version | Git Commit | Row Count | Column Count | File Size (Bytes) | MD5 Content Hash | Change Description | Restoration Verified? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Dataset v1** | `d3cd345` | 1,000 | 7 | 29,471 | `97b598979077e57ee23f92b1df98f64c` | Initial baseline housing dataset | **Yes** (Row count: 1000) |
| **Dataset v2** | `cc96759` | 1,200 | 7 | 35,360 | `97829b793eda583603f32986d3cafdd6` | Added 200 home sales transactions | **Yes** (Row count: 1200) |
| **Dataset v3** | `bd04b2d` | 1,350 | 7 | 39,788 | `ad83e64c9df3ec44461e94fe98811107` | Added 150 recent 2024 market listings | **Yes** (Row count: 1350) |

**Verification Questions:**
1. *How did you verify that DVC restored the intended version?*
   - Executed `git checkout <commit_sha> data/dataset.csv.dvc` followed by `dvc checkout`. Verified that the file size, MD5 checksum in `.dvc`, and actual dataframe shape in Python (`len(df)`) matched the target version exactly (e.g. 1000 rows for v1, 1350 rows for v3).
2. *Why is a filename alone insufficient to identify a dataset version?*
   - A filename (e.g. `dataset.csv`) is mutable and provides zero guarantees about contents. Two files with the exact same name can have completely different records, corrupted values, or drifted distributions. A cryptographic content hash (MD5) is required to guarantee reproducibility.

---

## 6. Part C: Integration of Git, DVC, and MLflow

### Tool Responsibility Matrix

| Tool | What it Tracks / Records | Where Information Lives | Why it Matters |
| :--- | :--- | :--- | :--- |
| **Git** | Source code, pipeline manifests (`dvc.yaml`), configs (`config.yaml`), and `.dvc` pointer files. | `.git/` repository tree and remote (e.g. GitHub). | Guarantees code versioning, commit histories, branching, and audit trails. |
| **DVC** | Large data files (`dataset.csv`), intermediate pipeline artifacts (`train.csv`, `test.csv`), and execution hashes (`dvc.lock`). | `.dvc/cache/` locally and `../dvc-storage` (or cloud remote S3/GCS). | Decouples large binary data from Git while ensuring byte-level data reproducibility. |
| **MLflow** | Hyperparameters, metrics (MAE, RMSE, $R^2$), plots, model signatures, input examples, serialized models, and lifecycle aliases. | `mlflow.db` (SQLite) and `mlruns/` artifact repository. | Provides experiment comparison, model registry governance, and serving metadata. |

### How a Teammate Recovers the Full State to Investigate a Prediction

1. **Find Model Metadata:**
   The teammate queries the MLflow Model Registry for the model serving predictions:
   ```python
   import mlflow
   mlflow.set_tracking_uri("sqlite:///mlflow.db")
   client = mlflow.tracking.MlflowClient()
   prod_model = client.get_model_version_by_alias("HousePriceModel", "production")
   print("Production Run ID:", prod_model.run_id)
   ```
2. **Retrieve Exact Git & DVC Provenance:**
   The teammate reads the run tags logged during training:
   ```python
   run = client.get_run(prod_model.run_id)
   git_commit = run.data.tags["git_commit"]
   dvc_hash = run.data.tags["dvc_dataset_hash"]
   print(f"Git Commit: {git_commit} | DVC Data Hash: {dvc_hash}")
   ```
3. **Restore Exact Code & Dataset:**
   In terminal:
   ```bash
   # Checkout exact code commit
   git checkout <git_commit>

   # Pull byte-for-byte identical dataset from DVC remote
   dvc checkout
   # or: dvc pull
   ```
4. **Reproduce & Debug:**
   The teammate can rerun inference using the exact loaded model or reproduce training via `dvc repro`.

---

## 7. Step-by-Step Reproduction Guide

### Prerequisites
- Python 3.11 installed.
- Git and virtual environment tools available.

### Reproduction Commands
```bash
# 1. Activate Virtual Environment
source .venv/bin/activate

# 2. Verify DVC remote and pull dataset
dvc pull

# 3. Reproduce the complete pipeline (data preparation -> model training)
dvc repro

# 4. Run model evaluation against acceptance rules
python src/evaluate.py

# 5. Run lifecycle promotion (candidate -> production -> archived)
python src/promote.py

# 6. Launch MLflow UI to view tracking and model registry
mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5001 --host 127.0.0.1
# Open http://127.0.0.1:5001 in your browser
```

---

## 8. Challenges Encountered & Resolutions

1. **Scikit-Learn Serialization in MLflow 3.17:**
   - *Issue:* Modern MLflow defaults to `skops` serialization for security auditing, which raised an `UntrustedTypesFoundException` for decision tree pointers in tree ensembles (`sklearn.tree._tree.Tree`).
   - *Resolution:* Configured `serialization_format=mlflow.sklearn.SERIALIZATION_FORMAT_CLOUDPICKLE` in `src/train.py`, ensuring seamless persistence and cross-environment deserialization.
2. **Scikit-Learn 1.6 RMSE Parameter Deprecation:**
   - *Issue:* `mean_squared_error(..., squared=False)` was deprecated in recent scikit-learn releases.
   - *Resolution:* Updated code to calculate RMSE via `np.sqrt(mean_squared_error(y_test, preds))`.
3. **MLflow UI Headless Verification:**
   - *Issue:* MLflow React frontend utilizes active websocket polling, causing standard networkidle browser hooks to time out.
   - *Resolution:* Implemented Playwright automation with `domcontentloaded` wait states and explicit timeout delays, capturing crisp PNG screenshots for inclusion in report artifacts.
