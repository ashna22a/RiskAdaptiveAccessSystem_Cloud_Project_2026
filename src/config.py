"""Single source of truth for feature lists and constants.
Never hardcode these elsewhere — mismatch between training and
inference feature ordering is the #1 cause of endpoint failures."""

FEATURE_COLUMNS = [
    "user_role",
    "service_type",
    "department",
    "access_method",
    "device_type",
    "login_frequency",
    "session_duration",
    "time_since_last_login",
    "location_distance_km",
    "access_count_7d",
    "failed_attempts_24h",
    "session_requests",
    "is_off_hours",
    "location_mismatch",
    "device_mismatch",
]

CATEGORICAL_FEATURES = [
    "user_role",
    "service_type",
    "department",
    "access_method",
    "device_type",
]

NUMERICAL_FEATURES = [
    "login_frequency",
    "session_duration",
    "time_since_last_login",
    "location_distance_km",
    "access_count_7d",
    "failed_attempts_24h",
    "session_requests",
    "is_off_hours",
    "location_mismatch",
    "device_mismatch",
]

TARGET_COLUMN = "risk_level"
RISK_LABELS = {0: "ALLOW", 1: "CHALLENGE_MFA", 2: "DENY"}

RANDOM_SEED = 42
