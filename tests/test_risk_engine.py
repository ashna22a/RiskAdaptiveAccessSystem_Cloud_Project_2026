"""Unit tests for the rule + ML hybrid engine."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from risk_engine import GovernmentPolicyRules, RiskScoringEngine, BehavioralBaseline


def _fake_ml_invoker(user_context, service_context):
    """Returns a low-risk prediction by default."""
    return {
        "risk_level": 0,
        "recommendation": "ALLOW",
        "confidence": 0.9,
        "risk_probabilities": {"allow": 0.9, "challenge": 0.08, "deny": 0.02},
    }


def _base_user_ctx(**overrides):
    base = {
        "user_role": "citizen",
        "is_off_hours": 0,
        "location_mismatch": 0,
        "device_mismatch": 0,
        "failed_attempts_24h": 0,
        "location_distance_km": 0.0,
        "login_location": "Chennai",
        "device_id": "D1",
        "session_duration": 200.0,
        "hour": 10,
    }
    base.update(overrides)
    return base


def _base_svc_ctx(**overrides):
    base = {"service_type": "general_info", "department": "general"}
    base.update(overrides)
    return base


def test_critical_service_forces_mfa():
    decision, reason = GovernmentPolicyRules.evaluate(
        _base_user_ctx(user_role="citizen"),
        _base_svc_ctx(service_type="tax_filing"),
    )
    assert decision == 1 and "Critical service" in reason


def test_excessive_failed_attempts_denies():
    decision, reason = GovernmentPolicyRules.evaluate(
        _base_user_ctx(failed_attempts_24h=6), _base_svc_ctx()
    )
    assert decision == 2 and "failed" in reason


def test_impossible_travel_denies():
    decision, reason = GovernmentPolicyRules.evaluate(
        _base_user_ctx(location_distance_km=1500.0), _base_svc_ctx()
    )
    assert decision == 2 and "Impossible" in reason


def test_engine_returns_allow_for_benign_request():
    engine = RiskScoringEngine(ml_invoker=_fake_ml_invoker, baseline_tracker=BehavioralBaseline())
    result = engine.compute_risk("U1", _base_user_ctx(), _base_svc_ctx())
    assert result["recommendation"] in ("ALLOW", "CHALLENGE_MFA")


def test_engine_respects_policy_override():
    engine = RiskScoringEngine(ml_invoker=_fake_ml_invoker, baseline_tracker=BehavioralBaseline())
    result = engine.compute_risk(
        "U1", _base_user_ctx(failed_attempts_24h=10), _base_svc_ctx()
    )
    assert result["recommendation"] == "DENY"
    assert result["source"] == "policy_rule"
