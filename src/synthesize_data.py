# src/synthesize_data.py
"""
Generates the Cloud Access Security Dataset (CSAD) — a synthetic dataset
of government e-service access events with realistic correlations between
user context and risk level.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import argparse
import os

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)


# ---------- Population parameters ----------
USER_ROLES = ['citizen', 'gov_employee', 'admin']
USER_ROLE_PROBS = [0.60, 0.30, 0.10]

SERVICE_TYPES = ['general_info', 'tax_filing', 'benefits_application',
                 'identity_verification', 'license_renewal']
SERVICE_PROBS = [0.35, 0.20, 0.20, 0.15, 0.10]

DEPARTMENTS = ['general', 'finance', 'health', 'defense', 'education']
DEPARTMENT_PROBS = [0.40, 0.20, 0.15, 0.10, 0.15]

ACCESS_METHODS = ['web_portal', 'mobile_app', 'api']
ACCESS_PROBS = [0.60, 0.35, 0.05]

DEVICE_TYPES = ['browser', 'mobile', 'tablet', 'desktop_client']
DEVICE_PROBS = [0.45, 0.35, 0.10, 0.10]

# Indian metro cities with lat/lon for distance calc
LOCATIONS = {
    'Chennai':    (13.08, 80.27),
    'Mumbai':     (19.07, 72.87),
    'Delhi':      (28.61, 77.20),
    'Bangalore':  (12.97, 77.59),
    'Hyderabad':  (17.38, 78.48),
    'Kolkata':    (22.57, 88.36),
    'Pune':       (18.52, 73.85),
    'Ahmedabad':  (23.02, 72.57),
}


def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance in km."""
    R = 6371.0
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))


def assign_risk_level(row):
    """
    Deterministic risk label derived from features with controlled noise.
    This gives the model a learnable signal while remaining realistic.
    Returns: 0 (Allow), 1 (Challenge MFA), 2 (Deny)
    """
    score = 0.0
    score += 0.35 * row['is_off_hours']
    score += 0.30 * row['location_mismatch']
    score += 0.20 * row['device_mismatch']
    score += 0.15 * min(row['failed_attempts_24h'] / 5.0, 1.0)
    score += 0.10 * min(row['location_distance_km'] / 1000.0, 1.0)

    # Service criticality amplifies risk
    if row['service_type'] in ('tax_filing', 'identity_verification'):
        score += 0.10
    if row['department'] in ('finance', 'defense'):
        score += 0.10

    # Roles with more privilege are riskier when anomalous
    if row['user_role'] == 'admin' and row['location_mismatch']:
        score += 0.15

    # Add Gaussian noise to avoid trivially separable classes
    score += np.random.normal(0, 0.05)
    score = np.clip(score, 0, 1)

    if score < 0.35:
        return 0   # Allow
    elif score < 0.65:
        return 1   # Challenge MFA
    else:
        return 2   # Deny


def synthesize(num_records=50000, num_users=2000):
    """Generate num_records access events across num_users synthesized users."""

    # --- Build user profiles (persistent attributes) ---
    users = []
    for uid in range(num_users):
        home_city = np.random.choice(list(LOCATIONS.keys()))
        users.append({
            'user_id': f'U{uid:05d}',
            'user_role': np.random.choice(USER_ROLES, p=USER_ROLE_PROBS),
            'usual_location': home_city,
            'usual_device_id': f'DEV{np.random.randint(10000, 99999)}',
            'baseline_login_hour': np.random.choice(
                [9, 10, 11, 14, 15, 16, 20],  # business hours bias
                p=[0.15, 0.20, 0.15, 0.15, 0.15, 0.10, 0.10]
            ),
        })
    users_df = pd.DataFrame(users)

    # --- Generate access events ---
    records = []
    base_time = datetime(2025, 1, 1)

    for _ in range(num_records):
        user = users_df.sample(1).iloc[0]
        uid = user['user_id']

        # --- Timestamp: mostly business hours ---
        is_off_hours = bool(np.random.random() < 0.28)
        if is_off_hours:
            hour = int(np.random.choice([0, 1, 2, 3, 4, 5, 22, 23]))
        else:
            hour = int(np.clip(
                np.random.normal(user['baseline_login_hour'], 2), 7, 21
            ))

        timestamp = base_time + timedelta(
            days=int(np.random.randint(0, 180)),
            hours=int(hour),
            minutes=int(np.random.randint(0, 60))
        )

        # --- Location: usually home city ---
        location_mismatch = np.random.random() < 0.18
        if location_mismatch:
            login_city = np.random.choice(
                [c for c in LOCATIONS if c != user['usual_location']]
            )
        else:
            login_city = user['usual_location']

        # Distance from usual location
        lat1, lon1 = LOCATIONS[user['usual_location']]
        lat2, lon2 = LOCATIONS[login_city]
        distance = haversine_km(lat1, lon1, lat2, lon2)

        # --- Device ---
        device_mismatch = np.random.random() < 0.15
        if device_mismatch:
            device_id = f'DEV{np.random.randint(10000, 99999)}'
        else:
            device_id = user['usual_device_id']

        # --- Behavior metrics ---
        login_frequency = int(np.clip(np.random.poisson(12), 1, 60))
        session_duration = float(np.clip(np.random.gamma(2.5, 90), 20, 1800))
        time_since_last_login = float(np.clip(np.random.exponential(48), 0.5, 720))
        access_count_7d = int(np.clip(np.random.poisson(15), 1, 80))
        failed_attempts_24h = int(np.random.choice(
            [0, 1, 2, 3, 5], p=[0.70, 0.15, 0.08, 0.04, 0.03]
        ))
        session_requests = int(np.clip(np.random.poisson(25), 1, 200))

        record = {
            'user_id': uid,
            'timestamp': timestamp.isoformat(),
            'user_role': user['user_role'],
            'service_type': np.random.choice(SERVICE_TYPES, p=SERVICE_PROBS),
            'department': np.random.choice(DEPARTMENTS, p=DEPARTMENT_PROBS),
            'access_method': np.random.choice(ACCESS_METHODS, p=ACCESS_PROBS),
            'device_type': np.random.choice(DEVICE_TYPES, p=DEVICE_PROBS),
            'login_frequency': login_frequency,
            'session_duration': round(session_duration, 2),
            'time_since_last_login': round(time_since_last_login, 2),
            'location_distance_km': round(distance, 2),
            'access_count_7d': access_count_7d,
            'failed_attempts_24h': failed_attempts_24h,
            'session_requests': session_requests,
            'login_location': login_city,
            'usual_location': user['usual_location'],
            'device_id': device_id,
            'usual_device_id': user['usual_device_id'],
            'is_off_hours': int(is_off_hours),
            'location_mismatch': int(location_mismatch),
            'device_mismatch': int(device_mismatch),
        }
        records.append(record)

    df = pd.DataFrame(records)

    # --- Assign risk labels ---
    df['risk_level'] = df.apply(assign_risk_level, axis=1)

    # --- Inject 2% missing values to force real preprocessing ---
    for col in ['session_duration', 'login_frequency']:
        mask = np.random.random(len(df)) < 0.02
        df.loc[mask, col] = np.nan

    # --- Inject 1% duplicates ---
    dup_idx = np.random.choice(df.index, size=int(0.01 * len(df)), replace=False)
    df = pd.concat([df, df.loc[dup_idx]], ignore_index=True)

    return df


def split_and_save(df, out_dir='data/processed'):
    """Stratified split preserving class distribution."""
    from sklearn.model_selection import train_test_split
    os.makedirs(out_dir, exist_ok=True)

    train, temp = train_test_split(
        df, test_size=0.30, random_state=RANDOM_SEED, stratify=df['risk_level']
    )
    val, test = train_test_split(
        temp, test_size=0.50, random_state=RANDOM_SEED, stratify=temp['risk_level']
    )

    train.to_csv(f'{out_dir}/csad_train.csv', index=False)
    val.to_csv(f'{out_dir}/csad_val.csv', index=False)
    test.to_csv(f'{out_dir}/csad_test.csv', index=False)

    print(f"Train: {len(train)} | Val: {len(val)} | Test: {len(test)}")
    print(f"\nClass distribution (train):\n{train['risk_level'].value_counts(normalize=True)}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--num-records', type=int, default=50000)
    parser.add_argument('--num-users', type=int, default=2000)
    parser.add_argument('--out', type=str, default='data/processed')
    args = parser.parse_args()

    print(f"Synthesizing {args.num_records} records...")
    df = synthesize(args.num_records, args.num_users)

    # Also save the full unsplit dataset
    os.makedirs('data/raw', exist_ok=True)
    df.to_csv('data/raw/csad_full.csv', index=False)

    split_and_save(df, args.out)
    print(f"\nFull dataset: data/raw/csad_full.csv")
    print(f"Splits saved to: {args.out}/")
