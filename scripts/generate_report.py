import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            # Skip header/footer on title page
            return

        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#718096"))

        # Header
        self.drawString(54, 755, "MLOps Lab 4-5: Advanced MLflow & DVC Versioning")
        self.drawRightString(612 - 54, 755, "Student: Mandeep Nehra (24AI038)")
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(54, 747, 612 - 54, 747)

        # Footer
        self.line(54, 45, 612 - 54, 45)
        self.drawString(54, 32, "Confidential - Academic Submission | Scalable AI Lab")
        self.drawRightString(612 - 54, 32, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

def build_pdf(filename="Report.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=30,
        textColor=colors.HexColor("#1A365D"),
        alignment=1, # Center
        spaceAfter=15
    )

    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=13,
        leading=18,
        textColor=colors.HexColor("#2B6CB0"),
        alignment=1,
        spaceAfter=25
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=colors.HexColor("#1A365D"),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        "Code_Custom",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#1A202C")
    )

    table_header_style = ParagraphStyle(
        "TH",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=1
    )

    table_cell_style = ParagraphStyle(
        "TC",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#2D3748")
    )

    table_cell_bold = ParagraphStyle(
        "TCB",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#1A365D")
    )

    caption_style = ParagraphStyle(
        "Caption",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#4A5568"),
        alignment=1,
        spaceAfter=10
    )

    story = []

    # ==================== COVER / TITLE PAGE ====================
    story.append(Spacer(1, 40))
    story.append(Paragraph("LAB ASSIGNMENT 4–5 REPORT", title_style))
    story.append(Paragraph("Advanced MLflow Tracking & Lifecycle Management with DVC Data Versioning", subtitle_style))
    story.append(HRFlowable(width="80%", thickness=2, color=colors.HexColor("#2B6CB0"), spaceAfter=30))

    meta_data = [
        [Paragraph("<b>Student Name:</b>", body_style), Paragraph("Mandeep Nehra", body_style)],
        [Paragraph("<b>Roll Number:</b>", body_style), Paragraph("24AI038", body_style)],
        [Paragraph("<b>Course:</b>", body_style), Paragraph("Scalable AI & MLOps Laboratory (Sessions 4–5)", body_style)],
        [Paragraph("<b>Date of Submission:</b>", body_style), Paragraph("October 17, 2026", body_style)],
        [Paragraph("<b>Repository:</b>", body_style), Paragraph("SAL_Lab 4,5 (mlops-lab-4-5)", body_style)],
        [Paragraph("<b>Git Tracking Commit:</b>", body_style), Paragraph("<code>8900ac9</code> (Clean Working Tree)", code_style)],
        [Paragraph("<b>DVC Dataset Hash:</b>", body_style), Paragraph("<code>ad83e64c9df3ec44461e94fe98811107</code>", code_style)]
    ]
    t_meta = Table(meta_data, colWidths=[150, 280])
    t_meta.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 35))

    # Executive Summary Box
    exec_text = """<b>Core Engineering Question:</b> <i>Can another engineer identify the model that was deployed and recover the code and dataset version used to create it?</i><br/><br/>
    <b>Executive Answer:</b> Yes, deterministically. Through rigorous integration of Git (code & metadata), DVC (data versioning & remote cache), and MLflow (experiment tracking & model registry), any deployed model revision can be traced back to its immutable Git commit SHA and cryptographic dataset MD5 checksum, enabling 100% bit-for-bit operational reproducibility."""
    t_exec = Table([[Paragraph(exec_text, body_style)]], colWidths=[480])
    t_exec.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EBF8FF")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#3182CE")),
        ("PADDING", (0, 0), (-1, -1), 12)
    ]))
    story.append(t_exec)

    story.append(PageBreak())

    # ==================== SECTION 1: OBJECTIVES & ENVIRONMENT ====================
    story.append(Paragraph("1. Lab Objectives & Technical Environment", h1_style))
    story.append(Paragraph(
        "This laboratory extends reproducible ML workflows across Sessions 4 and 5 by establishing an end-to-end MLOps pipeline. "
        "The primary objectives include: logging experiment parameters and evaluation metrics; attaching model signatures and representative input examples; "
        "registering candidate models into the MLflow Model Registry; implementing an explicit promotion workflow across candidate, staging, production, and archived states; "
        "tracking dataset revisions using DVC alongside Git metadata; configuring remote data storage; recovering historical data versions; and demonstrating complete provenance tracing.",
        body_style
    ))

    env_table_data = [
        [Paragraph("Tool / Component", table_header_style), Paragraph("Version", table_header_style), Paragraph("Operational Function in Pipeline", table_header_style)],
        [Paragraph("Python", table_cell_bold), Paragraph("3.11.14", table_cell_style), Paragraph("Runtime environment & package execution", table_cell_style)],
        [Paragraph("MLflow", table_cell_bold), Paragraph("3.17.1", table_cell_style), Paragraph("Tracking runs, parameters, metrics, artifacts, signatures & Model Registry", table_cell_style)],
        [Paragraph("DVC (Data Version Control)", table_cell_bold), Paragraph("3.67.1", table_cell_style), Paragraph("Dataset tracking, MD5 pointer generation, remote synchronization, pipeline DAG", table_cell_style)],
        [Paragraph("Git", table_cell_bold), Paragraph("2.52.0", table_cell_style), Paragraph("Source code versioning, DVC metadata tracking (.dvc, dvc.lock)", table_cell_style)],
        [Paragraph("Scikit-Learn", table_cell_bold), Paragraph("1.6.1", table_cell_style), Paragraph("Model estimators (Ridge, Random Forest, Gradient Boosting)", table_cell_style)],
        [Paragraph("Pandas & NumPy", table_cell_bold), Paragraph("2.2.3 / 2.2.3", table_cell_style), Paragraph("Dataset preprocessing, feature engineering, and matrix operations", table_cell_style)]
    ]
    t_env = Table(env_table_data, colWidths=[110, 75, 315])
    t_env.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A365D")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("PADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
    ]))
    story.append(t_env)
    story.append(Spacer(1, 12))

    # ==================== SECTION 2: PART A - ADVANCED MLFLOW ====================
    story.append(Paragraph("2. Part A (Lab 4) — Advanced MLflow Experiments & Model Registry", h1_style))
    story.append(Paragraph(
        "<b>A1. Theory & Core Concepts:</b><br/>"
        "• <b>Model Signature:</b> Enforces input and output schemas (feature names, data types, shapes). It prevents runtime silent failures when incoming prediction requests deviate from training distributions.<br/>"
        "• <b>Artifacts:</b> Heavy objects and non-scalar outputs generated during a run (e.g., serialized weights, residual plots, feature importance bar charts, JSON evaluation reports, and configuration files).<br/>"
        "• <b>Autologging:</b> Automatically intercepts supported ML framework training calls (e.g. <code>mlflow.sklearn.autolog()</code>) to record parameters, validation metrics, and fitted estimators without tedious manual instrumentations.<br/>"
        "• <b>Model Registry:</b> A collaborative hub managing registered model names, versions, lifecycle aliases (<code>@production</code>, <code>@staging</code>), tags, and validation history.<br/>"
        "• <b>Version vs. Stage / Alias:</b> A <i>version</i> is an immutable revision number (Version 1, 2, 3) representing a specific training artifact. A <i>stage/alias</i> (e.g. <code>@production</code>) is a mutable semantic pointer indicating operational deployment status.",
        body_style
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>A3. Experiment Comparison & Registered Models:</b>", h2_style))
    story.append(Paragraph(
        "Three distinct candidate models were trained on the Ames/Realistic Housing Price dataset (features: <code>OverallQual</code>, <code>GrLivArea</code>, <code>TotalBsmtSF</code>, <code>GarageCars</code>, <code>FullBath</code>, <code>YearBuilt</code>; target: <code>SalePrice</code>).",
        body_style
    ))

    model_table_data = [
        [Paragraph("Version", table_header_style), Paragraph("Model Architecture", table_header_style), Paragraph("Run ID", table_header_style), Paragraph("MAE ($)", table_header_style), Paragraph("RMSE ($)", table_header_style), Paragraph("R²", table_header_style), Paragraph("Promotion Decision", table_header_style)],
        [Paragraph("<b>v1</b>", table_cell_style), Paragraph("Ridge Regression (alpha=1.0)", table_cell_style), Paragraph("<code>a5598995303f</code>", code_style), Paragraph("$12,348", table_cell_style), Paragraph("$15,130", table_cell_style), Paragraph("0.9057", table_cell_style), Paragraph("<b>Archived</b> (Linear baseline)", table_cell_style)],
        [Paragraph("<b>v2</b>", table_cell_style), Paragraph("Random Forest (120 trees, d=8)", table_cell_style), Paragraph("<code>70d67fcf0a63</code>", code_style), Paragraph("$14,673", table_cell_style), Paragraph("$18,050", table_cell_style), Paragraph("0.8658", table_cell_style), Paragraph("<b>Staging / Candidate</b>", table_cell_style)],
        [Paragraph("<b>v3</b>", table_cell_style), Paragraph("Gradient Boosting (160 trees, lr=0.08, d=5)", table_cell_style), Paragraph("<code>1b998eb1e09d</code>", code_style), Paragraph("$13,829", table_cell_style), Paragraph("$17,136", table_cell_style), Paragraph("0.8790", table_cell_style), Paragraph("<b>Promoted to Production</b>", table_cell_bold)]
    ]
    t_model = Table(model_table_data, colWidths=[30, 135, 80, 50, 50, 40, 115])
    t_model.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A365D")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
    ]))
    story.append(t_model)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>A4. Model Signature & Robustness Discussion:</b>", h2_style))
    story.append(Paragraph(
        "The model was logged with a strict schema signature inferred from the training split:<br/>"
        "• <b>Inputs:</b> <code>[OverallQual: integer, GrLivArea: integer, TotalBsmtSF: integer, GarageCars: integer, FullBath: integer, YearBuilt: integer]</code><br/>"
        "• <b>Outputs:</b> <code>[SalePrice: double]</code><br/>"
        "• <b>Discussion Prompt:</b> <i>What could happen if a model expects four numeric columns but a future API sends three columns or changes a column type?</i><br/>"
        "In uninstrumented deployments, scikit-learn models will throw a low-level dimension mismatch error or produce corrupted mathematical inferences if types silently coerce. With MLflow model signatures, incoming REST/gRPC prediction requests are validated by the model server before invocation. If any column is missing or type-mismatched, the request fails fast with an informative HTTP 400 response.<br/>"
        "• <b>Limitation:</b> A signature verifies structural data types and column existence, but <b>cannot guarantee semantic validity</b> (e.g., negative square footage, impossible years, or out-of-distribution drift).",
        body_style
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>A6. Lifecycle Management & Promotion Rationale:</b>", h2_style))
    story.append(Paragraph(
        "<b>Acceptance Rule:</b> A model is eligible for production promotion if and only if $R^2 \\ge 0.85$, $\\text{RMSE} \\le \\$25,000$, and $\\text{MAE} \\le \\$20,000$.<br/>"
        "<b>Promotion Execution:</b> Version 3 (Gradient Boosting) achieved an $R^2$ of 0.8790 and RMSE of $17,136.26, easily passing acceptance. It was designated with the <code>@production</code> alias. Version 2 was assigned the <code>@staging</code> alias for shadow evaluation, and Version 1 was designated with <code>@archived</code>.<br/>"
        "<b>Critical Thinking Prompt:</b> <i>Should the highest-accuracy model always be promoted?</i><br/>"
        "No. Model promotion requires multi-criteria decision making. High accuracy on validation data can mask overfitting, data leakage, or class imbalance issues. Furthermore, real-world deployment requires balancing <b>inference latency</b> (tree depth / ensemble size), <b>computational hosting cost</b>, <b>robustness to missing inputs</b>, <b>explainability</b>, and <b>asymmetric business error costs</b> (e.g. overvaluing vs undervaluing a property).",
        body_style
    ))

    story.append(PageBreak())

    # ==================== SECTION 3: PART B - DATA VERSIONING WITH DVC ====================
    story.append(Paragraph("3. Part B (Lab 5) — Data Versioning with DVC", h1_style))
    story.append(Paragraph(
        "<b>B1. Core Theory:</b><br/>"
        "• <b>Why Git is not ideal for large datasets:</b> Git stores file revisions as internal packfile objects in the <code>.git</code> repository. Committing large binary files causes severe repository bloat, sluggish network clones, and out-of-memory errors.<br/>"
        "• <b>What DVC tracks vs. Data Remote:</b> DVC decouples large data from Git. Git tracks small, human-readable metadata pointer files (e.g., <code>dataset.csv.dvc</code> containing content hashes and byte sizes), while the actual dataset contents are cached locally in <code>.dvc/cache</code> and pushed to external shared storage (e.g. local directory remote, AWS S3, or GCS).<br/>"
        "• <b>Difference between Git commit and DVC version:</b> A Git commit captures the state of the codebase and DVC pointer files. A DVC data version is identified by an immutable content hash (MD5) representing the exact binary content of the dataset.",
        body_style
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>B6. Dataset Versions & Recovery Verification Table:</b>", h2_style))
    dvc_table_data = [
        [Paragraph("Dataset Version", table_header_style), Paragraph("Git Commit", table_header_style), Paragraph("Rows", table_header_style), Paragraph("Cols", table_header_style), Paragraph("File Size", table_header_style), Paragraph("MD5 Checksum", table_header_style), Paragraph("Change Description", table_header_style), Paragraph("Verified?", table_header_style)],
        [Paragraph("<b>Dataset v1</b>", table_cell_bold), Paragraph("<code>d3cd345</code>", code_style), Paragraph("1,000", table_cell_style), Paragraph("7", table_cell_style), Paragraph("29,471 B", table_cell_style), Paragraph("<code>97b598979077...</code>", code_style), Paragraph("Baseline housing dataset", table_cell_style), Paragraph("<b>Yes</b> (1000 rows)", table_cell_style)],
        [Paragraph("<b>Dataset v2</b>", table_cell_bold), Paragraph("<code>cc96759</code>", code_style), Paragraph("1,200", table_cell_style), Paragraph("7", table_cell_style), Paragraph("35,360 B", table_cell_style), Paragraph("<code>97829b793eda...</code>", code_style), Paragraph("Added 200 sales transactions", table_cell_style), Paragraph("<b>Yes</b> (1200 rows)", table_cell_style)],
        [Paragraph("<b>Dataset v3</b>", table_cell_bold), Paragraph("<code>bd04b2d</code>", code_style), Paragraph("1,350", table_cell_style), Paragraph("7", table_cell_style), Paragraph("39,788 B", table_cell_style), Paragraph("<code>ad83e64c9df3...</code>", code_style), Paragraph("Added 150 recent listings", table_cell_style), Paragraph("<b>Yes</b> (1350 rows)", table_cell_style)]
    ]
    t_dvc = Table(dvc_table_data, colWidths=[65, 55, 35, 30, 50, 85, 115, 65])
    t_dvc.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A365D")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
    ]))
    story.append(t_dvc)
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "<b>Restoration Verification Answers:</b><br/>"
        "• <i>How did you verify that DVC restored the intended version?</i><br/>"
        "We checked out commit <code>d3cd345</code> for <code>data/dataset.csv.dvc</code>, then executed <code>dvc checkout</code>. We verified via Python that the resulting <code>data/dataset.csv</code> had exactly 1,000 rows and matched the MD5 hash <code>97b598...</code>. We then restored <code>HEAD</code> (commit <code>bd04b2d</code>), executed <code>dvc checkout</code>, and confirmed the dataset restored to 1,350 rows and MD5 <code>ad83e6...</code>.<br/>"
        "• <i>Why is a filename alone insufficient to identify a dataset version?</i><br/>"
        "A filename is merely a pointer to a mutable storage location. Two files with the exact same name (<code>dataset.csv</code>) may have completely different rows, missing values, or modified targets. Only an immutable cryptographic content hash guarantees exact dataset version identity.",
        body_style
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>B7. DVC Pipelines & DAG:</b>", h2_style))
    story.append(Paragraph(
        "A multi-stage pipeline was codified in <code>dvc.yaml</code>:<br/>"
        "1. <b>Stage 'prepare':</b> Depends on <code>data/dataset.csv</code>, <code>configs/config.yaml</code>, <code>src/data_prep.py</code>; Outputs <code>data/train.csv</code>, <code>data/test.csv</code>.<br/>"
        "2. <b>Stage 'train':</b> Depends on prepared splits, <code>src/train.py</code>; Outputs evaluation figures and logs runs into MLflow.<br/>"
        "Executing <code>dvc repro</code> automatically re-computes only modified stages based on file hash changes in <code>dvc.lock</code>.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # ==================== SECTION 4: PART C - INTEGRATION ====================
    story.append(Paragraph("4. Part C — Integration of Git, DVC, and MLflow", h1_style))
    integ_data = [
        [Paragraph("Tool", table_header_style), Paragraph("What it Tracks / Records", table_header_style), Paragraph("Where Information Lives", table_header_style), Paragraph("Why it Matters in MLOps", table_header_style)],
        [Paragraph("<b>Git</b>", table_cell_bold), Paragraph("Source code, configs (<code>config.yaml</code>), DVC pointer files (<code>.dvc</code>, <code>dvc.lock</code>)", table_cell_style), Paragraph("<code>.git/</code> repository tree and remote host (GitHub)", table_cell_style), Paragraph("Guarantees code versioning, branch management, and collaborative review.", table_cell_style)],
        [Paragraph("<b>DVC</b>", table_cell_bold), Paragraph("Dataset versions, raw files, pipeline outputs, data caches, dependency DAG", table_cell_style), Paragraph("<code>.dvc/cache/</code> and remote storage (<code>../dvc-storage</code>)", table_cell_style), Paragraph("Enables large data versioning without repository bloat; guarantees byte-identical data recovery.", table_cell_style)],
        [Paragraph("<b>MLflow</b>", table_cell_bold), Paragraph("Hyperparameters, metrics (MAE, RMSE, R²), plots, signatures, model weights, registry aliases", table_cell_style), Paragraph("<code>mlflow.db</code> (SQLite backend) and <code>mlruns/</code> artifact store", table_cell_style), Paragraph("Centralizes experiment tracking, model registry lifecycle governance, and serving metadata.", table_cell_style)]
    ]
    t_integ = Table(integ_data, colWidths=[55, 145, 125, 175])
    t_integ.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A365D")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("PADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
    ]))
    story.append(t_integ)
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "<b>Investigation Workflow: How a teammate recovers the exact code, dataset, and model:</b><br/>"
        "1. <b>Query Model Registry:</b> Identify the production model via <code>client.get_model_version_by_alias('HousePriceModel', 'production')</code>. This reveals <code>Version 3</code> and Run ID <code>1b998eb1e09d...</code>.<br/>"
        "2. <b>Extract Provenance Tags:</b> Inspect the run tags in MLflow to retrieve <code>git_commit = bd04b2d...</code> and <code>dvc_dataset_hash = ad83e64c9df3...</code>.<br/>"
        "3. <b>Restore Code & Data:</b> Execute <code>git checkout bd04b2d</code> and <code>dvc checkout</code>. This immediately restores the identical Python code, pipeline definition, and byte-for-byte exact 1,350-row dataset.<br/>"
        "4. <b>Audit or Retrain:</b> Load the registered model weights directly via <code>models:/HousePriceModel@production</code> or run <code>dvc repro</code> to verify bit-level reproducibility.",
        body_style
    ))

    story.append(PageBreak())

    # ==================== SECTION 5: SCREENSHOTS & ARTIFACTS ====================
    story.append(Paragraph("5. Visual Evidence & MLflow UI Captures", h1_style))
    story.append(Paragraph(
        "The following screenshots were automatically captured from the live MLflow Tracking Server and Model Registry running on <code>http://127.0.0.1:5001</code>:",
        body_style
    ))
    story.append(Spacer(1, 4))

    # Add screenshots if they exist
    ss1 = "reports/screenshots/01_mlflow_experiments_runs.png"
    ss3 = "reports/screenshots/03_mlflow_registered_versions_aliases.png"
    if os.path.exists(ss1):
        story.append(Image(ss1, width=480, height=180))
        story.append(Paragraph("<b>Figure 1:</b> MLflow Experiments Overview showing candidate runs (Ridge, Random Forest, Gradient Boosting) with tracked metrics (MAE, RMSE, R²).", caption_style))

    if os.path.exists(ss3):
        story.append(Image(ss3, width=480, height=185))
        story.append(Paragraph("<b>Figure 2:</b> MLflow Model Registry for 'HousePriceModel' displaying Version 1, 2, 3 and aliases (@production, @staging, @archived).", caption_style))

    story.append(PageBreak())

    story.append(Paragraph("5. Visual Evidence & Artifacts (Continued)", h1_style))
    ss4 = "reports/screenshots/04_mlflow_run_artifacts_signature.png"
    if os.path.exists(ss4):
        story.append(Image(ss4, width=480, height=185))
        story.append(Paragraph("<b>Figure 3:</b> MLflow Run Detail view showcasing logged Model Signature, Input Examples, and tracked provenance tags (git_commit, dvc_dataset_hash).", caption_style))

    fig_res = "reports/figures/residual_plot_gradient_boosting.png"
    fig_imp = "reports/figures/feature_importance_gradient_boosting.png"
    if os.path.exists(fig_res) and os.path.exists(fig_imp):
        t_figs = Table([
            [Image(fig_res, width=235, height=140), Image(fig_imp, width=235, height=140)],
            [Paragraph("<b>Figure 4a:</b> Residual Plot (Gradient Boosting)", caption_style), Paragraph("<b>Figure 4b:</b> Feature Importance Plot", caption_style)]
        ], colWidths=[240, 240])
        t_figs.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
        story.append(t_figs)

    story.append(Spacer(1, 10))

    # ==================== SECTION 6: REFLECTIONS & REFERENCES ====================
    story.append(Paragraph("6. Challenges Encountered, Lessons Learned & References", h1_style))
    story.append(Paragraph(
        "<b>Challenges Encountered & Engineering Solutions:</b><br/>"
        "1. <b>MLflow 3.17 Skops Security Policy:</b> Modern MLflow utilizes <code>skops</code> by default for model persistence. Serializing tree estimators (such as <code>RandomForestRegressor</code> and <code>GradientBoostingRegressor</code>) resulted in <code>UntrustedTypesFoundException: ['sklearn.tree._tree.Tree']</code>. <i>Solution:</i> Explicitly configured <code>serialization_format=mlflow.sklearn.SERIALIZATION_FORMAT_CLOUDPICKLE</code> in <code>src/train.py</code> to ensure standard pickling without security false positives in our controlled lab environment.<br/>"
        "2. <b>Scikit-Learn 1.6 Deprecation:</b> <code>mean_squared_error(squared=False)</code> was removed in recent releases. <i>Solution:</i> Refactored RMSE calculation to <code>np.sqrt(mean_squared_error(y_true, y_pred))</code>.<br/>"
        "3. <b>Headless UI Verification:</b> Automated screenshot capture timed out due to active background polling in MLflow's React frontend. <i>Solution:</i> Configured Playwright with <code>domcontentloaded</code> synchronization and fixed render delays.<br/><br/>"
        "<b>Conclusion:</b><br/>"
        "The project demonstrates that combining Git, DVC, and MLflow resolves the core provenance dilemma of machine learning operations. By tying code commits to data checksums and model registry aliases, ML engineers can confidently deploy models, verify input schemas, and guarantee historical repeatability.<br/><br/>"
        "<b>References:</b><br/>"
        "1. MLflow Documentation: Model Registry, Signatures & Tracking — <i>https://mlflow.org/docs/latest/</i><br/>"
        "2. DVC Documentation: Data Versioning, Remotes & Pipelines — <i>https://dvc.org/doc</i><br/>"
        "3. Google Machine Learning Guide: Rules of Machine Learning & MLOps Architecture.",
        body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Report successfully compiled to {filename}")

if __name__ == "__main__":
    build_pdf()
