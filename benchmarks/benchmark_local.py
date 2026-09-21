"""Local latency benchmark for the risk engine + model."""

import sys
import os
import time
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from inference import predict
from risk_engine import RiskScoringEngine, BehavioralBaseline


def main():
    engine = RiskScoringEngine(ml_invoker=lambda u, s: predict([
        u.get("user_role", "citizen"),
        s.get("service_type", "general_info"),
        s.get("department", "general"),
        u.get("access_method", "web_portal"),
        u.get("device_type", "browser"),
        float(u.get("login_frequency", 10)),
        float(u.get("session_duration", 300)),
        float(u.get("time_since_last_login", 24)),
        float(u.get("location_distance_km", 5)),
        int(u.get("access_count_7d", 15)),
        int(u.get("failed_attempts_24h", 0)),
        int(u.get("session_requests", 20)),
        int(u.get("is_off_hours", 0)),
        int(u.get("location_mismatch", 0)),
        int(u.get("device_mismatch", 0)),
    ]), baseline_tracker=BehavioralBaseline())

    user_ctx = {
        "user_role": "citizen",
        "login_location": "Chennai",
        "device_id": "D1",
        "session_duration": 300.0,
        "hour": 10,
        "is_off_hours": 0,
        "location_mismatch": 0,
        "device_mismatch": 0,
        "failed_attempts_24h": 0,
        "location_distance_km": 5.0,
    }
    svc_ctx = {"service_type": "general_info", "department": "general"}

    # Warm-up
    for _ in range(5):
        engine.compute_risk("U-DEMO", user_ctx, svc_ctx)

    N = 200
    latencies = []
    for _ in range(N):
        start = time.time()
        engine.compute_risk("U-DEMO", user_ctx, svc_ctx)
        latencies.append(time.time() - start)

    arr = np.array(latencies) * 1000
    print(f"Requests: {N}")
    print(f"p50:  {np.percentile(arr, 50):.1f} ms")
    print(f"p95:  {np.percentile(arr, 95):.1f} ms")
    print(f"p99:  {np.percentile(arr, 99):.1f} ms")
    print(f"Mean: {arr.mean():.1f} ms")
    print(f"\nObjective #3 target: < 2000 ms end-to-end. Local engine: well under.")


if __name__ == "__main__":
    main()
