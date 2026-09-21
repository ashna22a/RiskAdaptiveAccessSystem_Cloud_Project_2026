"""Launch a Bayesian hyperparameter search.
Run from repo root:  python sagemaker/hyperparameter_tuning.py
"""

import sagemaker
from sagemaker.sklearn.estimator import SKLearn
from sagemaker.tuner import (
    IntegerParameter,
    CategoricalParameter,
    HyperparameterTuner,
)

session = sagemaker.Session()
role = sagemaker.get_execution_role()
bucket = session.default_bucket()
prefix = "zero-trust-csad"

train_s3 = session.upload_data(
    path="data/processed/csad_train.csv",
    bucket=bucket,
    key_prefix=f"{prefix}/train",
)
val_s3 = session.upload_data(
    path="data/processed/csad_val.csv",
    bucket=bucket,
    key_prefix=f"{prefix}/validation",
)

estimator = SKLearn(
    entry_point="train.py",
    source_dir="src",
    role=role,
    instance_type="ml.c5.xlarge",
    instance_count=1,
    framework_version="1.2-1",
    py_version="py3",
    hyperparameters={
        "n-estimators": 100,
        "max-depth": 15,
        "min-samples-leaf": 5,
        "max-features": "sqrt",
    },
    use_spot_instances=True,
    max_wait=3600,
    max_run=1800,
)

hyperparameter_ranges = {
    "n-estimators": IntegerParameter(50, 300),
    "max-depth": IntegerParameter(5, 30),
    "min-samples-leaf": IntegerParameter(1, 10),
    "max-features": CategoricalParameter(["sqrt", "log2", 0.5]),
}

metric_definitions = [
    {"Name": "validation:accuracy", "Regex": r"Validation Accuracy: ([0-9\.]+)"},
    {"Name": "validation:f1", "Regex": r"Validation F1 \(weighted\): ([0-9\.]+)"},
]

tuner = HyperparameterTuner(
    estimator=estimator,
    objective_metric_name="validation:accuracy",
    hyperparameter_ranges=hyperparameter_ranges,
    metric_definitions=metric_definitions,
    max_jobs=20,
    max_parallel_jobs=4,
    strategy="Bayesian",
    objective_type="Maximize",
    base_tuning_job_name="zero-trust-rf-tune",
)

tuner.fit({"train": train_s3, "validation": val_s3}, wait=True, logs=False)

print(f"\nBest training job: {tuner.best_training_job()}")
print(f"Best hyperparameters: {tuner.best_estimator().hyperparameters()}")

with open("sagemaker/best_tuning_job.txt", "w") as f:
    f.write(tuner.best_training_job())

print("Wrote best job name to sagemaker/best_tuning_job.txt")
