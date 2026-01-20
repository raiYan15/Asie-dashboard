from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from asie.forecast import run_forecasts

if __name__ == "__main__":
    run_forecasts(processed_root=ROOT / "data" / "processed", periods_ahead=6)
