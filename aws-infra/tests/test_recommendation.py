import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "lambdas" / "recommendation"))
from lambda_function import lambda_handler


def run(role="employee", fails=0, dist=5, off=0, service="general_info", dept="general"):
    return lambda_handler({
        "user_context": {
            "user_role": role,
            "failed_attempts_24h": fails,
            "location_distance_km": dist,
            "is_off_hours": off,
        },
        "service_context": {"service_type": service, "department": dept},
    }, None)


class RecommendationRules(unittest.TestCase):
    def test_allow_when_no_rule_fires(self):
        self.assertEqual(run()["recommendation"], "ALLOW")

    def test_citizen_on_critical_service_needs_mfa(self):
        self.assertEqual(run(role="citizen", service="tax_filing")["recommendation"], "CHALLENGE_MFA")

    def test_failed_attempts_beat_mfa(self):
        self.assertEqual(run(role="citizen", fails=6, service="tax_filing")["recommendation"], "DENY")

    def test_impossible_travel_is_denied(self):
        self.assertEqual(run(dist=1200)["recommendation"], "DENY")

    def test_off_hours_high_risk_department_needs_mfa(self):
        self.assertEqual(run(off=1, dept="finance")["recommendation"], "CHALLENGE_MFA")


if __name__ == "__main__":
    unittest.main()
