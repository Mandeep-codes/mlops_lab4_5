import os
import subprocess
import json
import yaml
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import mlflow
import mlflow.sklearn
from mlflow.models.signature import infer_signature
from mlflow.tracking import MlflowClient

from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Set plot style
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

def get_git_commit():
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8").strip()
        return commit
    except Exception as e:
        return "unknown_git_commit"

def get_dvc_hash(dvc_file="data/dataset.csv.dvc"):
    try:
        with open(dvc_file, "r") as f:
            dvc_data = yaml.safe_load(f)
            return dvc_data["outs"][0]["md5"]
    except Exception as e:
        return "unknown_dvc_hash"

def load_config(config_path="configs/config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def generate_residual_plot(y_true, y_pred, model_name, save_path):
    residuals = y_true - y_pred
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(y_pred, residuals, alpha=0.6, color="#1f77b4", edgecolors="k", s=30)
    ax.axhline(0, color="#d62728", linestyle="--", linewidth=1.5)
    ax.set_title(f"Residual Plot - {model_name}", fontsize=14, fontweight="bold")
    ax.set_xlabel("Predicted SalePrice ($)", fontsize=11)
    ax.set_ylabel("Residuals ($)", fontsize=11)
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig.savefig(save_path, dpi=200)
    plt.close(fig)

def generate_feature_importance_plot(model, feature_names, model_name, save_path):
    fig, ax = plt.subplots(figsize=(8, 5))
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
        indices = np.argsort(importances)
        ax.barh(range(len(indices)), importances[indices], color="#2ca02c", align="center")
        ax.set_yticks(range(len(indices)))
        ax.set_yticklabels([feature_names[i] for i in indices])
        ax.set_xlabel("Relative Importance", fontsize=11)
        ax.set_title(f"Feature Importance - {model_name}", fontsize=14, fontweight="bold")
    elif hasattr(model, "coef_"):
        coefs = model.coef_
        indices = np.argsort(np.abs(coefs))
        ax.barh(range(len(indices)), coefs[indices], color="#9467bd", align="center")
        ax.set_yticks(range(len(indices)))
        ax.set_yticklabels([feature_names[i] for i in indices])
        ax.set_xlabel("Coefficient Weight", fontsize=11)
        ax.set_title(f"Model Coefficients - {model_name}", fontsize=14, fontweight="bold")
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig.savefig(save_path, dpi=200)
    plt.close(fig)

def train_and_evaluate_all():
    config = load_config()
    tracking_uri = config.get("tracking_uri", "sqlite:///mlflow.db")
    experiment_name = config.get("experiment_name", "HousePricePrediction_Lab45")
    reg_model_name = config.get("registered_model_name", "HousePriceModel")

    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)
    client = MlflowClient()

    git_commit = get_git_commit()
    dvc_hash = get_dvc_hash()

    train_df = pd.read_csv(config["data"]["train_path"])
    test_df = pd.read_csv(config["data"]["test_path"])
    features = config["data"]["features"]
    target = config["data"]["target"]

    X_train = train_df[features]
    y_train = train_df[target]
    X_test = test_df[features]
    y_test = test_df[target]

    input_example = X_train.head(3)
    signature = infer_signature(X_train, y_train)

    models_to_train = [
        ("ridge", "v1", Ridge(alpha=config["models"]["ridge"]["alpha"])),
        ("random_forest", "v2", RandomForestRegressor(
            n_estimators=config["models"]["random_forest"]["n_estimators"],
            max_depth=config["models"]["random_forest"]["max_depth"],
            min_samples_split=config["models"]["random_forest"]["min_samples_split"],
            random_state=config["models"]["random_forest"]["random_state"]
        )),
        ("gradient_boosting", "v3", GradientBoostingRegressor(
            n_estimators=config["models"]["gradient_boosting"]["n_estimators"],
            learning_rate=config["models"]["gradient_boosting"]["learning_rate"],
            max_depth=config["models"]["gradient_boosting"]["max_depth"],
            random_state=config["models"]["gradient_boosting"]["random_state"]
        ))
    ]

    results = []

    print("=================================================================")
    print("STARTING MLFLOW TRAINING & REGISTRATION PIPELINE")
    print(f"Git Commit ID: {git_commit}")
    print(f"DVC Data Hash: {dvc_hash}")
    print("=================================================================")

    for model_key, target_version, model in models_to_train:
        m_cfg = config["models"][model_key]
        model_name = m_cfg["model_name"]
        intended_use = m_cfg["intended_use"]

        run_name = f"Run_{model_name}_{target_version}"

        with mlflow.start_run(run_name=run_name) as run:
            run_id = run.info.run_id
            print(f"\n[RUN] Training {model_name} (Run ID: {run_id})...")

            # Fit model
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            # Calculate metrics
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)

            # Log metrics manually
            mlflow.log_metric("mae", mae)
            mlflow.log_metric("rmse", rmse)
            mlflow.log_metric("r2_score", r2)

            # Log parameters
            mlflow.log_params(m_cfg)
            mlflow.log_param("model_type", type(model).__name__)
            mlflow.log_param("n_train_samples", len(X_train))
            mlflow.log_param("n_test_samples", len(X_test))
            mlflow.log_param("features_list", ",".join(features))

            # Set tags for provenance & student info
            mlflow.set_tag("student_name", "Mandeep Nehra")
            mlflow.set_tag("student_roll_no", "24AI038")
            mlflow.set_tag("git_commit", git_commit)
            mlflow.set_tag("dvc_dataset_hash", dvc_hash)
            mlflow.set_tag("intended_use", intended_use)
            mlflow.set_tag("target_version", target_version)
            mlflow.set_tag("dataset_version", "v3 (1350 rows)")

            # Generate and log artifacts
            res_plot_path = f"reports/figures/residual_plot_{model_key}.png"
            feat_plot_path = f"reports/figures/feature_importance_{model_key}.png"
            generate_residual_plot(y_test, y_pred, model_name, res_plot_path)
            generate_feature_importance_plot(model, features, model_name, feat_plot_path)

            mlflow.log_artifact(res_plot_path, artifact_path="figures")
            mlflow.log_artifact(feat_plot_path, artifact_path="figures")
            mlflow.log_artifact("configs/config.yaml", artifact_path="configs")

            # Evaluation report artifact
            eval_report = {
                "model_name": model_name,
                "target_version": target_version,
                "run_id": run_id,
                "git_commit": git_commit,
                "dvc_hash": dvc_hash,
                "metrics": {
                    "mae": round(float(mae), 2),
                    "rmse": round(float(rmse), 2),
                    "r2": round(float(r2), 4)
                },
                "acceptance_pass": bool(r2 >= config["acceptance_criteria"]["min_r2"] and rmse <= config["acceptance_criteria"]["max_rmse"])
            }
            report_path = f"reports/figures/eval_report_{model_key}.json"
            with open(report_path, "w") as f:
                json.dump(eval_report, f, indent=4)
            mlflow.log_artifact(report_path, artifact_path="reports")

            # Log model with signature and input example
            mlflow.sklearn.log_model(
                sk_model=model,
                artifact_path="model",
                signature=signature,
                input_example=input_example,
                registered_model_name=reg_model_name,
                serialization_format=mlflow.sklearn.SERIALIZATION_FORMAT_CLOUDPICKLE
            )

            print(f"[METRICS] MAE: ${mae:,.2f} | RMSE: ${rmse:,.2f} | R²: {r2:.4f}")
            print(f"[STATUS] Logged artifacts and registered to '{reg_model_name}'")

            results.append({
                "model_key": model_key,
                "model_name": model_name,
                "version": target_version,
                "run_id": run_id,
                "mae": mae,
                "rmse": rmse,
                "r2": r2,
                "intended_use": intended_use
            })

    # Summary table
    res_df = pd.DataFrame(results)
    print("\n=================== EXPERIMENT RUNS SUMMARY ===================")
    print(res_df[["version", "model_name", "run_id", "mae", "rmse", "r2"]])
    print("===============================================================")
    return res_df

if __name__ == "__main__":
    train_and_evaluate_all()
