# src/risk_engine.py

class GovernmentPolicyRules:
    CRITICAL_SERVICES = {'tax_filing', 'benefits_application', 'identity_verification'}
    HIGH_RISK_DEPARTMENTS = {'finance', 'defense', 'health'}

    @staticmethod
    def evaluate(user_context, service_context):
        user_role       = user_context.get('user_role', 'citizen')
        service_type    = service_context.get('service_type', 'general_info')
        department      = service_context.get('department', 'general')
        failed_attempts = int(user_context.get('failed_attempts_24h', 0))
        distance        = float(user_context.get('location_distance_km', 0))

        if 'is_off_hours' in user_context:
            is_off_hours = int(user_context['is_off_hours'])
        else:
            hour = int(user_context.get('hour', 12))
            is_off_hours = 1 if (hour < 6 or hour > 22) else 0

        # --- HARD BLOCKS (DENY) FIRST ---
        if failed_attempts >= 5:
            return 2, "Excessive failed authentication attempts"

        if distance > 1000:
            return 2, "Impossible travel detected"

        # --- SOFT CHALLENGES (MFA) SECOND ---
        if service_type in GovernmentPolicyRules.CRITICAL_SERVICES and user_role == 'citizen':
            return 1, "Critical service: MFA required for citizens"

        if is_off_hours == 1 and department in GovernmentPolicyRules.HIGH_RISK_DEPARTMENTS:
            return 1, "Off-hours access to high-risk department"

        return None, None
