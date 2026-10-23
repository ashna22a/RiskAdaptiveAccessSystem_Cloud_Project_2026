# src/train.py
import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, f1_score, classification_report, confusion_matrix,
)

from config import TARGET_COLUMN


def train_model():
    train_df = pd.read_csv("data/processed/train.csv")
    val_df = pd.read_csv("data/processed/val.csv")

    X_train = train_df.drop(columns=[TARGET_COLUMN])
    y_train = train_df[TARGET_COLUMN]
    X_val = val_df.drop(columns=[TARGET_COLUMN])
    y_val = val_df[TARGET_COLUMN]

    print(f"Training on {len(X_train)} samples, {X_train.shape[1]} features")
    print(f"Validating on {len(X_val)} samples")

    rf = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,          # Let trees grow — ZTA-RAD is small
        min_samples_leaf=1,
        max_features="sqrt",
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    rf.fit(X_train, y_train)

    y_pred = rf.predict(X_val)
    acc = accuracy_score(y_val, y_pred)
    f1 = f1_score(y_val, y_pred, average="weighted")

    print("\n" + "=" * 50)
    print(f"Validation Accuracy: {acc:.4f}")
    print(f"Validation F1 (weighted): {f1:.4f}")
    print("=" * 50)
    print(classification_report(
        y_val, y_pred,
        target_names=["Allow", "Challenge MFA", "Deny"],
        zero_division=0,
    ))
    print(f"Confusion Matrix:\n{confusion_matrix(y_val, y_pred)}")

    # Feature importances
    print("\nTop 10 Features:")
    importances = pd.Series(rf.feature_importances_, index=X_train.columns)
    for name, imp in importances.nlargest(10).items():
        print(f"  {name:40s} {imp:.4f}")

    os.makedirs("models", exist_ok=True)
    joblib.dump(rf, "models/random_forest.joblib")
    print("\nModel saved to models/random_forest.joblib")


if __name__ == "__main__":
    train_model()
