"""Model performance tests. Skips if no trained model present."""

import os
import sys
import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import accuracy_score, classification_report

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from config import FEATURE_COLUMNS, TARGET_COLUMN

MODEL_PATH = "models/random_forest.joblib"
PREP_PATH = "models/preprocessor.joblib"
TEST_CSV = "data/processed/csad_test.csv"


@pytest.fixture
def model_and_data():
    if not all(os.path.exists(p) for p in [MODEL_PATH, PREP_PATH, TEST_CSV]):
        pytest.skip("Trained model or test data missing — run training first.")
    model = joblib.load(MODEL_PATH)
    preprocessor = joblib.load(PREP_PATH)
    df = pd.read_csv(TEST_CSV)
    X = preprocessor.transform(df[FEATURE_COLUMNS])
    y = df[TARGET_COLUMN].values
    return model, X, y


def test_accuracy_threshold(model_and_data):
    model, X, y = model_and_data
    acc = accuracy_score(y, model.predict(X))
    assert acc >= 0.80, f"Accuracy {acc:.4f} below 80% objective"


def test_high_risk_recall(model_and_data):
    model, X, y = model_and_data
    report = classification_report(y, model.predict(X), output_dict=True, zero_division=0)
    # label 2 = Deny; report keys are strings in sklearn
    deny_recall = report.get("2", {}).get("recall", 0.0)
    assert deny_recall >= 0.80, f"Deny-class recall {deny_recall:.4f} below 80%"


def test_false_positive_rate(model_and_data):
    model, X, y = model_and_data
    y_pred = model.predict(X)
    fp = ((y == 0) & (y_pred > 0)).sum()
    total_allow = (y == 0).sum()
    fpr = fp / total_allow if total_allow else 0
    assert fpr < 0.10, f"False positive rate {fpr:.4f} exceeds 10%"


def test_inference_latency(model_and_data):
    import time
    model, X, _ = model_and_data
    start = time.time()
    model.predict(X[:1])
    elapsed = time.time() - start
    assert elapsed < 0.5, f"Local inference {elapsed:.3f}s exceeds 500ms"
