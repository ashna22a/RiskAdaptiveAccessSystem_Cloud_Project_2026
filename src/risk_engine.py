# src/risk_engine.py
# (This is exactly the same as before, but kept here for completeness)

class GovernmentPolicyRules:
    CRITICAL_SERVICES = {'tax_filing', 'benefits_application', 'identity_verification'}
    HIGH_RISK_DEPARTMENTS = {'finance', 'defense', 'health'}

    @staticmethod
    def evaluate(user_context, service_context):
        if (service_context['service_type'] in GovernmentPolicyRules.CRITICAL_SERVICES
            and user_context['user_role'] == 'citizen'):
            return 1, "Critical service: MFA required for citizens"
        
        if (user_context['is_off_hours'] == 1
            and service_context['department'] in GovernmentPolicyRules.HIGH_RISK_DEPARTMENTS):
            return 1, "Off-hours access to high-risk department"
            
        if user_context['failed_attempts_24h'] >= 5:
            return 2, "Excessive failed authentication attempts"
            
        if user_context['location_distance_km'] > 1000:
            return 2, "Impossible travel detected"
            
        return None, None
