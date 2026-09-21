"""Local hyperparameter search using GridSearchCV.
Free alternative to sagemaker/hyperparameter_tuning.py."""

import os
import sys
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.metrics import accuracy_score, f1_score, classification_report

sys.path.insert(0, os.path.dirname(__file__))

from preprocessing import build_preprocessing_pipeline
from config import (
    CATEGORICAL_FEATURES, NUMERICAL_FEATURES,
    FEATURE_COLUMNS, TARGET_COLUMN, RANDOM_SEED,
)


def main():
    train_df = pd.read_csv("data/processed/csad_train.csv")
    val_df = pd.read_csv("data/processed/csad_val.csv")

    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df[TARGET_COLUMN]
    X_val = val_df[FEATURE_COLUMNS]
    y_val = val_df[TARGET_COLUMN]

    pipe = build_preprocessing_pipeline(CATEGORICAL_FEATURES, NUMERICAL_FEATURES)
    X_train_p = pipe.fit_transform(X_train)
    X_val_p = pipe.transform(X_val)

    # Smaller grid than SageMaker — GridSearchCV is exhaustive so keep it tight
    param_grid = {
        "n_estimators": [100, 200],
        "max_depth": [10, 15, 20],
        "min_samples_leaf": [1, 5, 10],
        "max_features": ["sqrt", "log2"],
    }

    print("Searching hyperparameters with 3-fold CV (this takes ~2–5 min)...")
    search = GridSearchCV(
        RandomForestClassifier(
            class_weight="balanced",
            random_state=RANDOM_SEED,
            n_jobs=-1,
        ),
        param_grid=param_grid,
        scoring="accuracy",
        cv=StratifiedKFold(n_splits=3, shuffle=True, random_state=RANDOM_SEED),
        n_jobs=-1,
        verbose=1,
    )
    search.fit(X_train_p, y_train)

    print(f"\nBest params: {search.best_params_}")
    print(f"Best CV accuracy: {search.best_score_:.4f}")

    # Evaluate on held-out validation set
    best_model = search.best_estimator_
    y_pred = best_model.predict(X_val_p)
    acc = accuracy_score(y_val, y_pred)
    f1 = f1_score(y_val, y_pred, average="weighted")
    print(f"\nValidation Accuracy: {acc:.4f}")
    print(f"Validation F1 (weighted): {f1:.4f}")
    print(classification_report(y_val, y_pred, target_names=["Allow", "Challenge MFA", "Deny"]))

    # Persist the best model
    os.makedirs("models", exist_ok=True)
    joblib.dump(best_model, "models/random_forest.joblib")
    joblib.dump(pipe, "models/preprocessor.joblib")
    print("\nSaved best model to models/")


if __name__ == "__main__":
    main()
