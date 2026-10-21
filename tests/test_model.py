import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="joblib")

import pytest
import pandas as pd
import joblib
from sklearn.metrics import accuracy_score, f1_score


def test_zta_rad_accuracy():
    """Replicates report Test T01: model accuracy ≥ 80% on held-out test data."""
    try:
        model = joblib.load("models/random_forest.joblib")
        test_df = pd.read_csv("data/processed/test.csv")
    except FileNotFoundError:
        pytest.skip("Model or test data missing. Run pipeline first.")

    X_test = test_df.drop(columns=["risk_level"])
    y_test = test_df["risk_level"]

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted")

    print(f"\n[Test Results] Test Accuracy: {acc:.4f}, Test F1: {f1:.4f}")
    assert acc >= 0.80, f"Accuracy {acc:.4f} below 80% objective"
