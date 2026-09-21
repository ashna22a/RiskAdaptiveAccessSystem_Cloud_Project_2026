# Cloud Access Security Dataset (CSAD)

## Provenance
Synthesized from public cloud security datasets and documented
government e-service access patterns. Generation script: `src/synthesize_data.py`.

## Files
| File | Records | Purpose |
|------|---------|---------|
| raw/csad_full.csv | 50,000+ | Complete dataset before splitting |
| processed/csad_train.csv | 70% | Model training |
| processed/csad_val.csv | 15% | Hyperparameter tuning |
| processed/csad_test.csv | 15% | Final evaluation (never seen during training) |

## Schema (15 predictive features + metadata)
| # | Feature | Type | Description |
|---|---------|------|-------------|
| 1 | user_role | categorical | citizen / gov_employee / admin |
| 2 | service_type | categorical | e-service being accessed |
| 3 | department | categorical | Department owning the service |
| 4 | access_method | categorical | web_portal / mobile_app / api |
| 5 | device_type | categorical | browser / mobile / tablet / desktop_client |
| 6 | login_frequency | numerical | Logins in last 30 days |
| 7 | session_duration | numerical | Seconds |
| 8 | time_since_last_login | numerical | Hours |
| 9 | location_distance_km | numerical | From usual location |
| 10 | access_count_7d | numerical | Accesses in last 7 days |
| 11 | failed_attempts_24h | numerical | Failed auth attempts |
| 12 | session_requests | numerical | Requests in current session |
| 13 | is_off_hours | binary | 1 if outside 6am–10pm |
| 14 | location_mismatch | binary | 1 if login ≠ usual location |
| 15 | device_mismatch | binary | 1 if device ≠ usual device |

**Target:** `risk_level` — 0 (Allow), 1 (Challenge MFA), 2 (Deny)

## Preprocessing Required
1. Missing value imputation (median for numerical)
2. Deduplication on (user_id, timestamp)
3. Feature engineering (risk indicators)
4. One-hot encoding of categoricals
5. StandardScaler on numericals
6. Class balancing via `class_weight='balanced'`

## License
Academic use only.
