# run_pipeline.py
import subprocess
import sys
import os

def run(script_path):
    print(f"\n{'='*50}\nRunning {script_path}...\n{'='*50}")
    result = subprocess.run([sys.executable, script_path])
    if result.returncode != 0:
        print(f"Error running {script_path}. Stopping.")
        sys.exit(1)

if __name__ == "__main__":
    if not os.path.exists("data/raw/zta_rad.csv"):
        print("ERROR: Place the Mendeley ZTA-RAD CSV at data/raw/zta_rad.csv first.")
        sys.exit(1)
        
    run("src/preprocess.py")
    run("src/train.py")
    
    print("\n" + "="*50)
    print("Pipeline complete! Running tests...")
    print("="*50)
    subprocess.run(["pytest", "tests/", "-v", "-s"])
