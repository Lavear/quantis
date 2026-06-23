"""Generate dataset (if missing) and train the Random Forest forecaster."""
import os, sys, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from app.services.ml_forecast import train

CSV = os.path.join(os.path.dirname(__file__), "..", "dataset", "users.csv")
if not os.path.exists(CSV):
    subprocess.run([sys.executable, "generate_dataset.py"],
                   cwd=os.path.join(os.path.dirname(__file__), "..", "dataset"), check=True)
print(train(CSV))
