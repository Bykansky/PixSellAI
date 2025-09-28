# backend/scripts/quickstart_inference_wrapper.py
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[2] / ".env")
from app.models.inference_wrapper import generate_ensemble

# test image (можно взять frontend/static/sample1.jpg)
sample = Path("frontend/static/sample1.jpg")
if not sample.exists():
    raise SystemExit("Put sample image at frontend/static/sample1.jpg")

b = sample.read_bytes()
outs = generate_ensemble(b, style="modern", out_dir="backend/results/test_run", n_variants=2)
print("Results:", outs)
