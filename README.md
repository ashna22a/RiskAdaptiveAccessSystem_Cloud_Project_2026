# Zero Trust Cloud Access Recommendation System
### Risk-Adaptive Intelligence for Government e-Services

This repository contains the Machine Learning and Risk Engine implementation for our BCSE355L Cloud Architecture Design project. The system is designed to secure government e-services by moving away from static, binary access control. Instead, it uses a hybrid approach—combining deterministic government policy rules with a Random Forest machine learning classifier—to evaluate cloud access requests in real-time and output a graded recommendation: **ALLOW**, **CHALLENGE_MFA**, or **DENY**.

The model is trained on the ZTA-RAD dataset, analyzing 34 behavioral features (logon patterns, device usage, and HTTP access metrics) to detect anomalies and calculate risk.

**Team 13:** Ashna Agarwal (24BIT0249) and Krithikha B (24BIT0545)  
**Institution:** Vellore Institute of Technology  
**Course:** Cloud Architecture Design (BCSE355L)

---

## 🚀 How to Run This Project

Follow these three steps to download the dataset, install dependencies, and run the complete preprocessing and training pipeline.

### Step 1: Download the Dataset
We use the **ZTA-RAD** dataset from Mendeley Data. Due to licensing terms, the raw CSV is not committed to this repository. 

1. Go to **[Mendeley Data: ZTA-RAD](https://data.mendeley.com/datasets/d6hvsrxdts/1)**.
2. Download the CSV file.
3. Create a folder named `raw` inside `data/` (if it doesn't exist).
4. Rename the downloaded file to `zta_rad.csv` and place it exactly here: **`data/raw/zta_rad.csv`**.

*(See `data/README.md` for full details on the dataset schema, features, and preprocessing logic.)*

### Step 2: Install Requirements
Ensure you have Python 3.10+ installed. Open your terminal, navigate to the root of this project, and run:

```bash
# Create and activate a virtual environment (recommended)
python -m venv .venv
# Windows: .\.venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate

# Install the required Python packages
pip install -r requirements.txt
