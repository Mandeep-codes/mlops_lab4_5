import os
import time
from playwright.sync_api import sync_playwright

def capture_mlflow_screenshots():
    os.makedirs("reports/screenshots", exist_ok=True)
    base_url = "http://127.0.0.1:5001"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1400, "height": 900})
        page = context.new_page()

        print("[SCREENSHOT 1] Capturing MLflow Experiments & Runs table...")
        page.goto(f"{base_url}/#/experiments/1", wait_until="domcontentloaded")
        page.wait_for_timeout(4000)
        page.screenshot(path="reports/screenshots/01_mlflow_experiments_runs.png", full_page=False)
        print("-> Saved reports/screenshots/01_mlflow_experiments_runs.png")

        print("[SCREENSHOT 2] Capturing MLflow Models List...")
        page.goto(f"{base_url}/#/models", wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        page.screenshot(path="reports/screenshots/02_mlflow_model_registry_list.png", full_page=False)
        print("-> Saved reports/screenshots/02_mlflow_model_registry_list.png")

        print("[SCREENSHOT 3] Capturing MLflow Registered Model Versions & Aliases...")
        page.goto(f"{base_url}/#/models/HousePriceModel", wait_until="domcontentloaded")
        page.wait_for_timeout(4000)
        page.screenshot(path="reports/screenshots/03_mlflow_registered_versions_aliases.png", full_page=False)
        print("-> Saved reports/screenshots/03_mlflow_registered_versions_aliases.png")

        print("[SCREENSHOT 4] Capturing MLflow Run Details & Artifacts...")
        page.goto(f"{base_url}/#/experiments/1", wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        try:
            # Click on the gradient boosting run
            row = page.locator("a:has-text('GradientBoosting')").first
            if row.count() > 0:
                row.click()
                page.wait_for_timeout(4000)
            page.screenshot(path="reports/screenshots/04_mlflow_run_artifacts_signature.png", full_page=False)
            print("-> Saved reports/screenshots/04_mlflow_run_artifacts_signature.png")
        except Exception as e:
            print("Fallback for screenshot 4:", e)
            page.screenshot(path="reports/screenshots/04_mlflow_run_artifacts_signature.png", full_page=False)

        browser.close()
    print("All screenshots successfully captured!")

if __name__ == "__main__":
    capture_mlflow_screenshots()
