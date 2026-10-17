import os
import yaml
import pandas as pd
from sklearn.model_selection import train_test_split

def load_config(config_path="configs/config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def prepare_data(config_path="configs/config.yaml"):
    config = load_config(config_path)
    raw_path = config["data"]["raw_path"]
    train_path = config["data"]["train_path"]
    test_path = config["data"]["test_path"]
    test_size = config["data"]["test_size"]
    random_state = config["data"]["random_state"]

    print(f"[DATA PREPARATION] Reading raw data from: {raw_path}")
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Raw data file not found at {raw_path}")

    df = pd.read_csv(raw_path)
    print(f"[DATA PREPARATION] Total raw records: {len(df)}, Features: {list(df.columns)}")

    train_df, test_df = train_test_split(df, test_size=test_size, random_state=random_state)

    os.makedirs(os.path.dirname(train_path), exist_ok=True)
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)

    print(f"[DATA PREPARATION] Saved train set: {train_path} ({len(train_df)} rows)")
    print(f"[DATA PREPARATION] Saved test set: {test_path} ({len(test_df)} rows)")

if __name__ == "__main__":
    prepare_data()
