from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from asie.pipeline import run_pipeline

if __name__ == "__main__":
    run_pipeline(
        geo_level="pincode",
        freq="M",
        raw_root=ROOT / "data" / "raw",
        processed_root=ROOT / "data" / "processed",
        report_path=ROOT / "reports" / "summary_pincode.md",
        anomaly_threshold=2.0,
    )
