"""Rule + ML hybrid risk engine used by the Lambda handler.
Provides behavioral baselining and government-policy overrides."""

import numpy as np
from collections import defaultdict


class BehavioralBaseline:
    """Per-user online statistics for anomaly scoring."""

    def __init__(self, decay_factor=0.95):
        self.decay_factor = decay_factor
        self.stats = defaultdict(
            lambda: {
                "login_count": 0,
                "login_hours": [],
                "locations": set(),
                "devices": set(),
                "mean_session_duration": 0.0,
                "std_session_duration": 1.0,
            }
        )

    def update(self, user_id, access_event):
        stat = self.stats[user_id]
        stat["login_count"] = stat["login_count"] * self.decay_factor + 1

        n = min(stat["login_count"], 100)
        delta = access_event["session_duration"] - stat["mean_session_duration"]
        stat["mean_session_duration"] += delta / n
        delta2 = access_event["session_duration"] - stat["mean_session_duration"]

        if n > 1:
            stat["std_session_duration"] = np.sqrt(
                (stat["std_session_duration"] ** 2 * (n - 1) + delta * delta2) / n
            )
        else:
            stat["std_session_duration"] = 1.0

        stat["locations"].add(access_event["login_location"])
        stat["devices"].add(access_event["device_id"])
        stat["login_hours"].append(access_event["hour"])

    def compute_anomaly_score(self, user_id, access_event):
        stat = self.stats[user_id]

        if stat["login_count"] < 5:
            return 0.5

        location_novelty = (
            0.0 if access_event["login_location"] in stat["locations"] else 0.4
        )
        device_novelty = 0.0 if access_event["device_id"] in stat["devices"] else 0.3

        if stat["std_session_duration"] > 0:
            duration_z = abs(
                access_event["session_duration"] - stat["mean_session_duration"]
            ) / stat["std_session_duration"]
            duration_anomaly = min(duration_z / 3.0, 1.0) * 0.2
        else:
            duration_anomaly = 0.1

        expected_hour = np.mean(stat["login_hours"]) if stat["login_hours"] else 12
        hour_deviation = min(abs(access_event["hour"] - expected_hour) / 12.0, 1.0) * 0.1

        return min(
            location_novelty + device_novelty + duration_anomaly + hour_deviation, 1.0
        )


class GovernmentPolicyRules:
    """Deterministic government-specific overrides."""

    CRITICAL_SERVICES = {"tax_filing", "benefits_application", "identity_verification"}
    HIGH_RISK_DEPARTMENTS = {"finance", "defense", "health"}

    @staticmethod
    def evaluate(user_context, service_context):
        if (
            service_context["service_type"] in GovernmentPolicyRules.CRITICAL_SERVICES
            and user_context["user_role"] == "citizen"
        ):
            return 1, "Critical service: MFA required for citizens"

        if (
            user_context["is_off_hours"] == 1
            and service_context["department"]
            in GovernmentPolicyRules.HIGH_RISK_DEPARTMENTS
        ):
            return 1, "Off-hours access to high-risk department"

        if user_context["failed_attempts_24h"] >= 5:
            return 2, "Excessive failed authentication attempts"

        if user_context["location_distance_km"] > 1000:
            return 2, "Impossible travel detected"

        return None, None


class RiskScoringEngine:
    """Combines policy rules, behavioral baselines, and ML predictions."""

    def __init__(self, ml_invoker, baseline_tracker):
        self.ml_invoker = ml_invoker
        self.baseline = baseline_tracker

    def compute_risk(self, user_id, user_context, service_context):
        factors = []

        override_decision, override_reason = GovernmentPolicyRules.evaluate(
            user_context, service_context
        )
        if override_decision is not None:
            return {
                "recommendation": ["ALLOW", "CHALLENGE_MFA", "DENY"][override_decision],
                "risk_score": 0.95 if override_decision == 2 else 0.7,
                "source": "policy_rule",
                "reason": override_reason,
                "factors": [override_reason],
            }

        anomaly_score = self.baseline.compute_anomaly_score(user_id, user_context)
        if anomaly_score > 0.5:
            factors.append(f"Behavioral anomaly detected (score: {anomaly_score:.2f})")

        ml_result = self.ml_invoker(user_context, service_context)
        combined_risk = self._combine_scores(ml_result, anomaly_score, user_context)

        return {
            "recommendation": self._risk_to_recommendation(combined_risk),
            "risk_score": combined_risk,
            "confidence": ml_result["confidence"],
            "source": "ml_model",
            "factors": factors,
            "ml_breakdown": ml_result["risk_probabilities"],
        }

    @staticmethod
    def _combine_scores(ml_result, anomaly_score, user_context):
        probs = ml_result["risk_probabilities"]
        ml_risk = probs["challenge"] * 0.5 + probs["deny"] * 1.0

        context_modifier = 0.0
        if user_context.get("is_off_hours"):
            context_modifier += 0.1
        if user_context.get("location_mismatch"):
            context_modifier += 0.15
        if user_context.get("device_mismatch"):
            context_modifier += 0.1

        return min(ml_risk * 0.6 + anomaly_score * 0.25 + context_modifier * 0.15, 1.0)

    @staticmethod
    def _risk_to_recommendation(risk_score):
        if risk_score < 0.4:
            return "ALLOW"
        if risk_score < 0.7:
            return "CHALLENGE_MFA"
        return "DENY"
