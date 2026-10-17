import os
import yaml
import json
import numpy as np
import pandas as pd
import mlflow
from mlflow.tracking import MlflowClient
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def load_config(config_path="configs/config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def evaluate_registered_models():
    config = load_config()
    tracking_uri = config.get("tracking_uri", "sqlite:///mlflow.db")
    reg_model_name = config.get("registered_model_name", "HousePriceModel")

    mlflow.set_tracking_uri(tracking_uri)
    client = MlflowClient()

    test_df = pd.read_csv(config["data"]["test_path"])
    features = config["data"]["features"]
    target = config["data"]["target"]

    X_test = test_df[features]
    y_test = test_df[target]

    acceptance = config["acceptance_criteria"]
    min_r2 = acceptance["min_r2"]
    max_rmse = acceptance["max_rmse"]
    max_mae = acceptance["max_mae"]

    print(f"\n=================== EVALUATING REGISTERED MODELS ===================")
    print(f"Registered Model: {reg_model_name}")
    print(f"Acceptance Rule: R² >= {min_r2} AND RMSE <= ${max_rmse:,.0f} AND MAE <= ${max_mae:,.0f}")
    print("====================================================================\n")

    versions = client.search_model_versions(f"name='{reg_model_name}'")
    eval_results = []

    for v in sorted(versions, key=lambda x: int(x.version)):
        v_num = v.version
        run_id = v.run_id
        model_uri = f"models:/{reg_model_name}/{v_num}"

        # Load registered model
        model = mlflow.sklearn.load_model(model_uri)
        y_pred = model.predict(X_test)

        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)

        passed = (r2 >= min_r2) and (rmse <= max_rmse) and (mae <= max_mae)

        eval_results.append({
            "version": f"v{v_num}",
            "version_num": v_num,
            "run_id": run_id,
            "mae": mae,
            "rmse": rmse,
            "r2": r2,
            "passed_acceptance": passed,
            "current_aliases": v.aliases,
            "status": v.status
        })

        print(f"-> Model Version v{v_num}:")
        print(f"   Run ID: {run_id}")
        print(f"   Aliases: {v.aliases}")
        print(f"   MAE: ${mae:,.2f} | RMSE: ${rmse:,.2f} | R²: {r2:.4f}")
        print(f"   Meets Acceptance Rule: {'PASSED [PROMOTION CANDIDATE]' if passed else 'FAILED'}\n")

    return eval_results

if __name__ == "__main__":
    evaluate_registered_models()
