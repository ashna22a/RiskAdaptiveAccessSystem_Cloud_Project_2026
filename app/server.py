# app/server.py
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, jsonify, render_template
from src.inference import predict
from src.risk_engine import GovernmentPolicyRules

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/assess', methods=['POST'])
def assess():
    data = request.get_json(force=True)

    user_context = {
        "user_role":            data.get("user_role", "citizen"),
        "hour":                 int(data.get("hour", 12)),
        "location_distance_km": float(data.get("location_distance_km", 0)),
        "login_frequency":      int(data.get("login_frequency", 12)),
        "failed_attempts_24h":  int(data.get("failed_attempts_24h", 0)),
    }
    service_context = {
        "service_type": data.get("service_type", "general_info"),
        "department":   data.get("department", "general"),
    }

    # 1. ALWAYS run the ML model to get probabilities for the UI
    ml_result = None
    try:
        ml_result = predict(data)
    except Exception as e:
        print(f"ML Model Error: {e}")

    # 2. Check the Rule Engine (Deterministic overrides)
    override_decision, override_reason = GovernmentPolicyRules.evaluate(
        user_context, service_context
    )

    # 3. Determine final decision
    if override_decision is not None:
        labels = {0: "ALLOW", 1: "CHALLENGE_MFA", 2: "DENY"}
        final_recommendation = labels[override_decision]
        final_reason = override_reason
        final_source = "policy_rule"
        final_risk_score = 0.95 if override_decision == 2 else 0.70
    elif ml_result is not None:
        final_recommendation = ml_result["recommendation"]
        final_reason = "Behavioral model prediction"
        final_source = "ml_model"
        probs = ml_result["probabilities"]
        final_risk_score = (probs["challenge"] * 0.5) + (probs["deny"] * 1.0)
    else:
        # Fallback if both failed
        final_recommendation = "ERROR"
        final_reason = "Backend failure"
        final_source = "error"
        final_risk_score = 0

    # 4. Return response (always include ML probabilities if they exist)
    probs = ml_result["probabilities"] if ml_result else {"allow": 0, "challenge": 0, "deny": 0}
    
    return jsonify({
        "source":         final_source,
        "recommendation": final_recommendation,
        "reason":         final_reason,
        "risk_score":     round(final_risk_score, 3),
        "confidence":     round(ml_result["confidence"], 3) if ml_result else 0,
        "probabilities":  probs,  # <--- This will now always populate!
    })


if __name__ == '__main__':
    if not os.path.exists("models/random_forest.joblib"):
        print("ERROR: Model not found. Run `python run_pipeline.py` first.")
        exit(1)

    print("\n" + "=" * 50)
    print("Zero Trust Demo running at: http://localhost:5000")
    print("=" * 50 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
