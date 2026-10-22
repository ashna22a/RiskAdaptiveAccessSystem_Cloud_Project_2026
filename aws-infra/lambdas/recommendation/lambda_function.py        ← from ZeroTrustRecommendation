CRITICAL_SERVICES = {"tax_filing", "benefits_application", "identity_verification"}
HIGH_RISK_DEPARTMENTS = {"finance", "defense", "health"}


def lambda_handler(event, context):
    user_context = event.get("user_context", {})
    service_context = event.get("service_context", {})

    # DENY rules are checked first, so a severe signal is never downgraded to MFA
    if int(user_context.get("failed_attempts_24h", 0)) >= 5:
        return decision("DENY", "Excessive failed authentication attempts", "policy_rule")

    if float(user_context.get("location_distance_km", 0)) > 1000:
        return decision("DENY", "Impossible travel detected", "policy_rule")

    # MFA rules
    if (service_context.get("service_type") in CRITICAL_SERVICES
            and user_context.get("user_role") == "citizen"):
        return decision("CHALLENGE_MFA", "Critical service: MFA required for citizens", "policy_rule")

    if (int(user_context.get("is_off_hours", 0)) == 1
            and service_context.get("department") in HIGH_RISK_DEPARTMENTS):
        return decision("CHALLENGE_MFA", "Off-hours access to high-risk department", "policy_rule")

    # No rule fired: the ML model will decide here once it is connected
    return decision("ALLOW", "No policy rule triggered; ML model not connected", "default_no_model")


def decision(recommendation, reason, source):
    return {
        "recommendation": recommendation,
        "reason": reason,
        "source": source
    }
