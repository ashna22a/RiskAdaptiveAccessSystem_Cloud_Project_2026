"""Launch a single SageMaker training job for quick iteration.
Run from repo root:  python sagemaker/launch_training.py
"""

import sagemaker
from sagemaker.sklearn.estimator import SKLearn

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
        "n-estimators": 200,
        "max-depth": 15,
        "min-samples-leaf": 5,
        "max-features": "sqrt",
    },
    use_spot_instances=True,
    max_wait=7200,
    max_run=3600,
)

estimator.fit({"train": train_s3, "validation": val_s3})
print(f"Model artifact: {estimator.model_data}")
