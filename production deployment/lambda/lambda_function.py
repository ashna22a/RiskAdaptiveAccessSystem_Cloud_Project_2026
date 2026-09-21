"""AWS Lambda handler for the Zero Trust risk scoring pipeline.
Expects env vars: SAGEMAKER_ENDPOINT, USER_TABLE, ALERT_TOPIC."""

import json
import os
from datetime import datetime

import boto3

sagemaker_runtime = boto3.client("sagemaker-runtime")
dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")

ENDPOINT_NAME = os.environ["SAGEMAKER_ENDPOINT"]
USER_TABLE = dynamodb.Table(os.environ["USER_TABLE"])
ALERT_TOPIC = os.environ["ALERT_TOPIC"]


def lambda_handler(event, context):
    """Event: {user_id, user_context, service_context}"""
    try:
        user_id = event["user_id"]
        user_profile = USER_TABLE.get_item(Key={"user_id": user_id}).get("Item", {})

        user_context = dict(event.get("user_context", {}))
        user_context.setdefault("user_role", user_profile.get("role", "citizen"))
        user_context.setdefault("usual_location", user_profile.get("usual_location", ""))

        service_context = event.get("service_context", {})

        risk_result = invoke_risk_model(user_context, service_context)
        final_decision = apply_policy_rules(user_context, service_context, risk_result)

        log_access_event(user_id, final_decision)

        if final_decision["recommendation"] == "DENY":
            send_security_alert(user_id, final_decision)

        return {"statusCode": 200, "body": json.dumps(final_decision)}

    except Exception as exc:
        print(f"Error processing access request: {exc}")
        return {
            "statusCode": 500,
            "body": json.dumps(
                {"error": "Risk assessment failed", "recommendation": "DENY"}
            ),
        }


def invoke_risk_model(user_context, service_context):
    """Build the 15-feature vector and call the SageMaker endpoint."""
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

    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=ENDPOINT_NAME,
        ContentType="application/json",
        Body=json.dumps({"features": features}),
    )
    return json.loads(response["Body"].read().decode())


def apply_policy_rules(user_context, service_context, ml_result):
    """Deterministic overrides take priority over ML prediction."""
    critical_services = {"tax_filing", "benefits_application", "identity_verification"}
    high_risk_depts = {"finance", "defense", "health"}

    if (
        service_context.get("service_type") in critical_services
        and user_context.get("user_role") == "citizen"
    ):
        return {
            "recommendation": "CHALLENGE_MFA",
            "reason": "Critical service: MFA required for citizens",
            "source": "policy_rule",
        }

    if (
        user_context.get("is_off_hours") == 1
        and service_context.get("department") in high_risk_depts
    ):
        return {
            "recommendation": "CHALLENGE_MFA",
            "reason": "Off-hours access to high-risk department",
            "source": "policy_rule",
        }

    if int(user_context.get("failed_attempts_24h", 0)) >= 5:
        return {
            "recommendation": "DENY",
            "reason": "Excessive failed authentication attempts",
            "source": "policy_rule",
        }

    if float(user_context.get("location_distance_km", 0)) > 1000:
        return {
            "recommendation": "DENY",
            "reason": "Impossible travel detected",
            "source": "policy_rule",
        }

    return ml_result


def log_access_event(user_id, decision):
    USER_TABLE.put_item(
        Item={
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "decision": decision.get("recommendation"),
            "risk_score": str(decision.get("risk_score", "")),
            "source": decision.get("source", ""),
        }
    )


def send_security_alert(user_id, decision):
    sns.publish(
        TopicArn=ALERT_TOPIC,
        Subject=f"[Zero Trust] High-risk access for {user_id}",
        Message=json.dumps(decision, indent=2),
    )
