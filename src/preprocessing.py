"""Data cleaning, feature engineering, and sklearn preprocessing pipeline."""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

from config import CATEGORICAL_FEATURES, NUMERICAL_FEATURES


def load_and_clean_data(filepath):
    """Load CSAD dataset and perform initial cleaning."""
    df = pd.read_csv(filepath)

    # Median imputation for numerical columns
    for col in ["login_frequency", "session_duration"]:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    # Deduplicate on (user_id, timestamp)
    df = df.drop_duplicates(subset=["user_id", "timestamp"])

    return df


def engineer_risk_features(df):
    """Create behavioral risk indicators from raw fields."""
    df = df.copy()

    df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour
    df["is_off_hours"] = ((df["hour"] < 6) | (df["hour"] > 22)).astype(int)
    df["location_mismatch"] = (
        df["login_location"] != df["usual_location"]
    ).astype(int)
    df["device_mismatch"] = (df["device_id"] != df["usual_device_id"]).astype(int)

    mean_freq = df["login_frequency"].mean()
    std_freq = df["login_frequency"].std() or 1.0
    df["frequency_zscore"] = (
        (df["login_frequency"] - mean_freq) / std_freq
    ).abs()

    df["behavioral_risk_score"] = (
        df["is_off_hours"] * 0.3
        + df["location_mismatch"] * 0.3
        + df["device_mismatch"] * 0.2
        + (df["frequency_zscore"] > 2).astype(int) * 0.2
    )

    return df


def build_preprocessing_pipeline(categorical_features=None, numerical_features=None):
    """Return a fit-ready ColumnTransformer."""
    categorical_features = categorical_features or CATEGORICAL_FEATURES
    numerical_features = numerical_features or NUMERICAL_FEATURES

    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numerical_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )
