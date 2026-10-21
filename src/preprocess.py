"""
Prepare ZTA-RAD for model training.

Steps:
  1. Load raw CSV
  2. Drop synthetic rows (sintetico == 1)
  3. Map 'risco' → integer class {0,1,2}
  4. Select ZTA_TRAIN_FEATURES + target
  5. Stratified 70/15/15 split
  6. SMOTE on training set only
  7. Save to data/processed/
"""
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE

from src.config import (
    RAW_DATA_PATH,
    PROCESSED_DIR,
    MODEL_DIR,
    TARGET_COLUMN,
    RISK_LABEL_MAP,
    ZTA_TRAIN_FEATURES,
    RANDOM_SEED,
)


def _parse_target(df: pd.DataFrame) -> pd.Series:
    """Map the 'risco' column to integer classes."""
    if "risco" not in df.columns:
        raise ValueError(f"Column 'risco' not found. Available: {df.columns.tolist()}")

    raw = df["risco"].astype(str).str.strip().str.lower()
    parsed = raw.map(RISK_LABEL_MAP)

    if parsed.isna().all():
        raise ValueError(f"No 'risco' values could be mapped. Unique: {raw.unique()[:10].tolist()}")

    unparsed = int(parsed.isna().sum())
    if unparsed > 0:
        print(f"  WARNING: dropping {unparsed} rows with unmapped 'risco' values")

    return parsed


def prepare():
    print(f"Loading {RAW_DATA_PATH}...")
    df = pd.read_csv(RAW_DATA_PATH)
    print(f"  Loaded {len(df)} rows, {len(df.columns)} columns")

    # Drop synthetic rows
    if "sintetico" in df.columns:
        before = len(df)
        df = df[df["sintetico"] == 0].copy()
        print(f"  Dropped {before - len(df)} synthetic rows → {len(df)} real rows")

    # Parse target
    df[TARGET_COLUMN] = _parse_target(df)
    df = df.dropna(subset=[TARGET_COLUMN])
    df[TARGET_COLUMN] = df[TARGET_COLUMN].astype(int)
    print(f"  Label distribution: {df[TARGET_COLUMN].value_counts().sort_index().to_dict()}")

    # Verify ZTA-RAD columns exist
    missing = [c for c in ZTA_TRAIN_FEATURES if c not in df.columns]
    if missing:
        raise ValueError(f"Missing ZTA-RAD columns: {missing}")

    # Prepare features
    X = df[ZTA_TRAIN_FEATURES].copy()
    for col in X.columns:
        X[col] = pd.to_numeric(X[col], errors="coerce")
    X = X.fillna(X.median(numeric_only=True)).fillna(0)
    y = df[TARGET_COLUMN].copy()

    # Stratified split
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, stratify=y, random_state=RANDOM_SEED
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=RANDOM_SEED
    )

    # SMOTE on training data only
    print(f"  Before SMOTE: {y_train.value_counts().sort_index().to_dict()}")
    k = min(5, int(y_train.value_counts().min()) - 1)
    if k >= 1:
        smote = SMOTE(random_state=RANDOM_SEED, k_neighbors=k)
        X_train, y_train = smote.fit_resample(X_train, y_train)
    print(f"  After SMOTE:  {y_train.value_counts().sort_index().to_dict()}")

    # Persist
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    pd.concat([X_train, y_train], axis=1).to_csv(f"{PROCESSED_DIR}/train.csv", index=False)
    pd.concat([X_val, y_val], axis=1).to_csv(f"{PROCESSED_DIR}/val.csv", index=False)
    pd.concat([X_test, y_test], axis=1).to_csv(f"{PROCESSED_DIR}/test.csv", index=False)

    # Save feature order for inference
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(ZTA_TRAIN_FEATURES, f"{MODEL_DIR}/feature_order.joblib")

    print(f"\n  Splits: train={len(X_train)}, val={len(X_val)}, test={len(X_test)}")
    print(f"  Features: {len(ZTA_TRAIN_FEATURES)}")
    print(f"  Saved to {PROCESSED_DIR}/")


if __name__ == "__main__":
    prepare()
