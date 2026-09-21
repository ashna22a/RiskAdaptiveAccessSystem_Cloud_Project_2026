"""Sanity tests for cleaning, feature engineering, and pipeline."""

import os
import sys
import pandas as pd
import pytest

# Make src/ importable when tests run from repo root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from preprocessing import (
    load_and_clean_data,
    engineer_risk_features,
    build_preprocessing_pipeline,
)


@pytest.fixture
def sample_df(tmp_path):
    df = pd.DataFrame(
        {
            "user_id": ["U1", "U1", "U2"],
            "timestamp": [
                "2025-01-01T10:00:00",
                "2025-01-01T10:00:00",
                "2025-01-02T22:30:00",
            ],
            "login_location": ["Chennai", "Chennai", "Delhi"],
            "usual_location": ["Chennai", "Chennai", "Chennai"],
            "device_id": ["D1", "D1", "D2"],
            "usual_device_id": ["D1", "D1", "D1"],
            "login_frequency": [10, None, 3],
            "session_duration": [300, 200, None],
        }
    )
    path = tmp_path / "sample.csv"
    df.to_csv(path, index=False)
    return str(path)


def test_cleaning_drops_duplicates_and_fills_nans(sample_df):
    df = load_and_clean_data(sample_df)
    assert len(df) == 2  # one duplicate removed
    assert df["login_frequency"].isna().sum() == 0
    assert df["session_duration"].isna().sum() == 0


def test_engineered_features_present(sample_df):
    df = engineer_risk_features(load_and_clean_data(sample_df))
    for col in ["is_off_hours", "location_mismatch", "device_mismatch", "behavioral_risk_score"]:
        assert col in df.columns


def test_pipeline_produces_dense_array(sample_df):
    df = engineer_risk_features(load_and_clean_data(sample_df))
    # Add required columns that build_preprocessing_pipeline expects
    df["user_role"] = "citizen"
    df["service_type"] = "tax_filing"
    df["department"] = "finance"
    df["access_method"] = "web_portal"
    df["device_type"] = "browser"
    for col in [
        "time_since_last_login",
        "location_distance_km",
        "access_count_7d",
        "failed_attempts_24h",
        "session_requests",
    ]:
        df[col] = 1.0

    pipe = build_preprocessing_pipeline()
    X = pipe.fit_transform(df)
    assert X.shape[0] == len(df)
