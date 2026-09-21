"""Flask demo server exposing the Zero Trust risk engine.
Run:  python app/server.py
Then open: http://localhost:5000
"""

import os
import sys
import json
from datetime import datetime

from flask import Flask, request, jsonify, render_template

# Make src/ importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from inference import predict                      # local predictor
from risk_engine import (                          # hybrid engine
    BehavioralBaseline,
    GovernmentPolicyRules,
    RiskScoringEngine,
)

app = Flask(__name__)

# In-memory baselines — reset when server restarts (fine for demo)
baselines = BehavioralBaseline()


def ml_invoker(user_context, service_context):
    """Adapter that turns context dicts into the 15-feature vector."""
    features = [
        user_context.get("user_role", "citizen"),
        service_context.get("service_type", "general_info"),
        service_context.get("department", "general"),
        user_context.get("access_method", "web_portal"),
        user_context.get("device_type", "browser"),
        float(user_context.get("login_frequency", 0)),
        float(user_context.get("session_duration", 0)),
        float(user_context.get("time_since_last_login", 0)),
        float(user_context.get("location_distance_km", 0)),
        int(user_context.get("access_count_7d", 0)),
        int(user_context.get("failed_attempts_24h", 0)),
        int(user_context.get("session_requests", 0)),
        int(user_context.get("is_off_hours", 0)),
        int(user_context.get("location_mismatch", 0)),
        int(user_context.get("device_mismatch", 0)),
    ]
    return predict(features)


engine = RiskScoringEngine(ml_invoker=ml_invoker, baseline_tracker=baselines)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/assess", methods=["POST"])
def assess():
    payload = request.get_json(force=True)
    user_id = payload.get("user_id", "U-DEMO")

    user_context = dict(payload.get("user_context", {}))
    service_context = dict(payload.get("service_context", {}))

    # Compute hour-based fields if not given
    hour = int(user_context.get("hour", datetime.now().hour))
    user_context.setdefault("hour", hour)
    user_context.setdefault("is_off_hours", int(hour < 6 or hour > 22))
    user_context.setdefault("location_mismatch", 0)
    user_context.setdefault("device_mismatch", 0)
    user_context.setdefault("user_role", "citizen")
    user_context.setdefault("login_location", "Chennai")
    user_context.setdefault("device_id", "DEV-DEMO")
    user_context.setdefault("session_duration", 300.0)

    result = engine.compute_risk(user_id, user_context, service_context)

    # Update baseline so subsequent requests from this user use fresh stats
    baselines.update(user_id, {
        "login_location": user_context["login_location"],
        "device_id": user_context["device_id"],
        "session_duration": float(user_context["session_duration"]),
        "hour": hour,
    })

    result["user_id"] = user_id
    result["timestamp"] = datetime.utcnow().isoformat()
    return jsonify(result)


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    # Make sure a model exists before starting
    if not os.path.exists("models/random_forest.joblib"):
        print("ERROR: models/random_forest.joblib not found.")
        print("Run `python src/train.py` first.")
        sys.exit(1)
    app.run(host="0.0.0.0", port=5000, debug=True)
