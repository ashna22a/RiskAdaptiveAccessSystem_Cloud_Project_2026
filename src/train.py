"""SageMaker training entry point.
Prints metric lines that the HyperparameterTuner regex matches."""

import argparse
import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report

from preprocessing import build_preprocessing_pipeline
from config import (
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    RANDOM_SEED,
)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=str, default=os.environ.get("SM_CHANNEL_TRAIN"))
    parser.add_argument(
        "--validation", type=str, default=os.environ.get("SM_CHANNEL_VALIDATION")
    )
    parser.add_argument(
        "--model-dir", type=str, default=os.environ.get("SM_MODEL_DIR", "models")
    )
    parser.add_argument("--n-estimators", type=int, default=100)
    parser.add_argument("--max-depth", type=int, default=15)
    parser.add_argument("--min-samples-leaf", type=int, default=5)
    parser.add_argument("--max-features", type=str, default="sqrt")
    return parser.parse_known_args()


def _parse_max_features(value):
    """Coerce SageMaker's string hyperparameters into sklearn-valid values."""
    if value in ("sqrt", "log2"):
        return value
    try:
        return float(value)
    except (TypeError, ValueError):
        return "sqrt"


def train(args):
    train_path = os.path.join(args.train, "csad_train.csv")
    val_path = os.path.join(args.validation, "csad_val.csv")

    train_df = pd.read_csv(train_path)
    val_df = pd.read_csv(val_path)

    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df[TARGET_COLUMN]
    X_val = val_df[FEATURE_COLUMNS]
    y_val = val_df[TARGET_COLUMN]

    preprocessor = build_preprocessing_pipeline(
        CATEGORICAL_FEATURES, NUMERICAL_FEATURES
    )
    X_train_p = preprocessor.fit_transform(X_train)
    X_val_p = preprocessor.transform(X_val)

    rf = RandomForestClassifier(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        min_samples_leaf=args.min_samples_leaf,
        max_features=_parse_max_features(args.max_features),
        class_weight="balanced",
        random_state=RANDOM_SEED,
        n_jobs=-1,
    )
    rf.fit(X_train_p, y_train)

    y_pred = rf.predict(X_val_p)
    accuracy = accuracy_score(y_val, y_pred)
    f1 = f1_score(y_val, y_pred, average="weighted")

    # --- These exact lines are parsed by the tuner regex ---
    print(f"Validation Accuracy: {accuracy:.4f}")
    print(f"Validation F1 (weighted): {f1:.4f}")
    # -------------------------------------------------------

    print(
        classification_report(
            y_val, y_pred, target_names=["Allow", "Challenge MFA", "Deny"]
        )
    )

    os.makedirs(args.model_dir, exist_ok=True)
    joblib.dump(rf, os.path.join(args.model_dir, "random_forest.joblib"))
    joblib.dump(preprocessor, os.path.join(args.model_dir, "preprocessor.joblib"))


# src/train.py (add at the bottom, replacing the __main__ block)
if __name__ == "__main__":
    import sys
    args, _ = parse_args()
    # If SM_CHANNEL_TRAIN isn't set, assume the standard local layout
    if args.train is None:
        args.train = "data/processed"
    if args.validation is None:
        args.validation = "data/processed"
    if args.model_dir is None or args.model_dir == "models":
        args.model_dir = "models"
    train(args)
    print(f"\nSaved model artifacts to: {args.model_dir}/")
