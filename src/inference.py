# src/inference.py
import joblib
import pandas as pd

from src.config import MODEL_DIR, RISK_LABELS, ZTA_TRAIN_FEATURES


_MODEL = None
_FEATURE_ORDER = None


def _load():
    global _MODEL, _FEATURE_ORDER
    if _MODEL is None:
        _MODEL = joblib.load(f"{MODEL_DIR}/random_forest.joblib")
        _FEATURE_ORDER = joblib.load(f"{MODEL_DIR}/feature_order.joblib")
    return _MODEL, _FEATURE_ORDER


def _fill_missing_features(payload: dict) -> dict:
    """
    If the payload already has ZTA-RAD features, use them as-is.
    Any ZTA-RAD feature missing from the payload is filled with a
    benign default so the model always sees a complete 34-feature row.
    """
    features = {}
    for col in ZTA_TRAIN_FEATURES:
        if col in payload:
            features[col] = payload[col]
        else:
            features[col] = 0  # Benign default — see scenario profiles for real values
    return features


def predict(payload: dict) -> dict:
    model, feature_order = _load()

    # Ensure all ZTA-RAD features present
    zta_features = _fill_missing_features(payload)

    # Build row in the order the model expects
    row = [zta_features.get(col, 0) for col in feature_order]
    df = pd.DataFrame([row], columns=feature_order)

    pred = int(model.predict(df)[0])
    probs = model.predict_proba(df)[0]

    return {
        "risk_level": pred,
        "recommendation": RISK_LABELS[pred],
        "confidence": float(max(probs)),
        "probabilities": {
            "allow": float(probs[0]) if len(probs) > 0 else 0.0,
            "challenge": float(probs[1]) if len(probs) > 1 else 0.0,
            "deny": float(probs[2]) if len(probs) > 2 else 0.0,
        },
    }
