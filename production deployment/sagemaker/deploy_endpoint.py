"""Deploy the best tuned model (or last trained model) as a real-time endpoint.
Run from repo root:  python sagemaker/deploy_endpoint.py
"""

import os
import sagemaker
from sagemaker.sklearn.model import SKLearnModel
from sagemaker import TrainingJob

session = sagemaker.Session()
role = sagemaker.get_execution_role()

# Prefer the best tuning job if it exists; else fall back to a manual job name
best_job_file = "sagemaker/best_tuning_job.txt"
if os.path.exists(best_job_file):
    with open(best_job_file) as f:
        job_name = f.read().strip()
    print(f"Using best tuning job: {job_name}")
else:
    raise FileNotFoundError(
        "sagemaker/best_tuning_job.txt not found. "
        "Run hyperparameter_tuning.py first or set a job name manually."
    )

best_job = TrainingJob(name=job_name, sagemaker_session=session)
model_data = best_job.model_data
print(f"Model artifact: {model_data}")

model = SKLearnModel(
    model_data=model_data,
    role=role,
    entry_point="inference.py",
    source_dir="src",
    framework_version="1.2-1",
    py_version="py3",
)

predictor = model.deploy(
    initial_instance_count=1,
    instance_type="ml.m5.large",
    endpoint_name="zero-trust-risk-scorer",
)
print(f"Endpoint deployed: {predictor.endpoint_name}")
