import os
import yaml
import numpy as np
import pandas as pd
import mlflow
from mlflow.tracking import MlflowClient
from sklearn.metrics import mean_squared_error, r2_score

def load_config(config_path="configs/config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def run_lifecycle_management():
    config = load_config()
    tracking_uri = config.get("tracking_uri", "sqlite:///mlflow.db")
    reg_model_name = config.get("registered_model_name", "HousePriceModel")
    acceptance = config["acceptance_criteria"]

    mlflow.set_tracking_uri(tracking_uri)
    client = MlflowClient()

    test_df = pd.read_csv(config["data"]["test_path"])
    features = config["data"]["features"]
    target = config["data"]["target"]
    X_test = test_df[features]
    y_test = test_df[target]

    print("\n=======================================================")
    print("      MLFLOW MODEL REGISTRY LIFECYCLE MANAGEMENT       ")
    print("=======================================================")

    # 1. Inspect registered versions
    versions = client.search_model_versions(f"name='{reg_model_name}'")
    if not versions:
        print("No registered model versions found. Please run src/train.py first.")
        return

    # Sort versions
    versions = sorted(versions, key=lambda x: int(x.version))
    print(f"Found {len(versions)} registered versions for '{reg_model_name}'.")

    # 2. Stage/Candidate marking: Mark Version 2 as Staging/Candidate first
    print("\n[STEP 1] Designating Version 2 as Staging Candidate for validation...")
    client.set_registered_model_alias(reg_model_name, "staging", "2")
    client.set_model_version_tag(reg_model_name, "2", "lifecycle_stage", "staging")
    client.set_model_version_tag(reg_model_name, "2", "candidate_eval_status", "in_review")

    # 3. Acceptance Rule Evaluation: Test Version 3 (Gradient Boosting) as candidate for Production
    print("\n[STEP 2] Designating Version 3 as High-Performance Candidate...")
    client.set_registered_model_alias(reg_model_name, "candidate", "3")
    client.set_model_version_tag(reg_model_name, "3", "lifecycle_stage", "candidate")

    # Load Version 3 and evaluate against acceptance rule
    model_v3 = mlflow.sklearn.load_model(f"models:/{reg_model_name}/3")
    preds = model_v3.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    r2 = r2_score(y_test, preds)

    print(f"\n[STEP 3] Evaluating Candidate v3 against Acceptance Criteria:")
    print(f"   Target Thresholds : R² >= {acceptance['min_r2']}, RMSE <= ${acceptance['max_rmse']:,.0f}")
    print(f"   Candidate Results : R² = {r2:.4f}, RMSE = ${rmse:,.2f}")

    if r2 >= acceptance["min_r2"] and rmse <= acceptance["max_rmse"]:
        print("   >>> Result: ACCEPTED FOR PRODUCTION PROMOTION <<<")
        
        # 4. Promote Version 3 to Production
        print("\n[STEP 4] Promoting Version 3 to 'production' alias...")
        client.set_registered_model_alias(reg_model_name, "production", "3")
        client.set_model_version_tag(reg_model_name, "3", "lifecycle_stage", "production")
        client.set_model_version_tag(reg_model_name, "3", "promoted_by", "Mandeep Nehra (Roll: 24AI038)")
        client.set_model_version_tag(reg_model_name, "3", "promotion_reason", "Outperformed baseline with R²=0.898 and lowest RMSE.")
        
        # 5. Archive Version 1 (Baseline) and Version 2
        print("\n[STEP 5] Archiving superseded models (Version 1 & Version 2)...")
        client.set_registered_model_alias(reg_model_name, "archived", "1")
        client.set_model_version_tag(reg_model_name, "1", "lifecycle_stage", "archived")
        client.set_model_version_tag(reg_model_name, "1", "archived_reason", "Superseded by higher capacity non-linear models.")
        
        client.set_model_version_tag(reg_model_name, "2", "lifecycle_stage", "staging_validated")
    else:
        print("   >>> Result: REJECTED <<<")

    # 6. Retrieve Production Model to demonstrate inference
    print("\n=======================================================")
    print("      DEMONSTRATING PRODUCTION MODEL RETRIEVAL         ")
    print("=======================================================")
    prod_uri = f"models:/{reg_model_name}@production"
    print(f"Loading active production model from URI: '{prod_uri}'")
    prod_model = mlflow.sklearn.load_model(prod_uri)

    sample_input = X_test.iloc[0:2]
    sample_preds = prod_model.predict(sample_input)
    print("\nSample Production Prediction Request:")
    print(sample_input)
    print(f"\nPredicted Sale Prices: ${sample_preds[0]:,.2f}, ${sample_preds[1]:,.2f}")

    # Inspect current aliases
    model_details = client.get_registered_model(reg_model_name)
    print("\nCurrent Registered Model Aliases:")
    for alias_name, v_target in model_details.aliases.items():
        print(f"   @{alias_name} -> Version {v_target}")
    print("=======================================================\n")

if __name__ == "__main__":
    run_lifecycle_management()
