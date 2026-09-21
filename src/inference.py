"""Local predictor — loads joblib artifacts and returns predictions.
Replaces the SageMaker inference.py path for the free demo."""

import json
import os
import joblib

RISK_LABELS = {0: "ALLOW", 1: "CHALLENGE_MFA", 2: "DENY"}

_MODEL = None
_PREPROCESSOR = None


def load_model(model_dir="models"):
    global _MODEL, _PREPROCESSOR
    if _MODEL is None:
        _MODEL = joblib.load(os.path.join(model_dir, "random_forest.joblib"))
        _PREPROCESSOR = joblib.load(os.path.join(model_dir, "preprocessor.joblib"))
    return _MODEL, _PREPROCESSOR


def predict(features):
    """features: list of 15 values in FEATURE_COLUMNS order."""
    model, preprocessor = load_model()
    X = preprocessor.transform([features])
    pred = int(model.predict(X)[0])
    probs = model.predict_proba(X)[0]
    return {
        "risk_level": pred,
        "recommendation": RISK_LABELS[pred],
        "confidence": float(max(probs)),
        "risk_probabilities": {
            "allow": float(probs[0]),
            "challenge": float(probs[1]),
            "deny": float(probs[2]),
        },
    }


# Keep model_fn / input_fn / predict_fn so the file is still valid
# if you later deploy it to SageMaker.
def model_fn(model_dir):
    model = joblib.load(os.path.join(model_dir, "random_forest.joblib"))
    preprocessor = joblib.load(os.path.join(model_dir, "preprocessor.joblib"))
    return {"model": model, "preprocessor": preprocessor}


def input_fn(request_body, content_type="application/json"):
    if content_type != "application/json":
        raise ValueError(f"Unsupported content type: {content_type}")
    return json.loads(request_body)


def predict_fn(input_data, model_dict):
    features = input_data["features"]
    X = model_dict["preprocessor"].transform([features])
    pred = int(model_dict["model"].predict(X)[0])
    probs = model_dict["model"].predict_proba(X)[0]
    return {
        "risk_level": pred,
        "recommendation": RISK_LABELS[pred],
        "confidence": float(max(probs)),
        "risk_probabilities": {
            "allow": float(probs[0]),
            "challenge": float(probs[1]),
            "deny": float(probs[2]),
        },
    }


def output_fn(prediction, accept="application/json"):
    return json.dumps(prediction)
