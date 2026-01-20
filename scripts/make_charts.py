from pathlib import Path
import sys

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

PLOTS_DIR = ROOT / "reports" / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def load_latest(metrics_path: Path, geo_cols):
    df = pd.read_parquet(metrics_path)
    latest = df[df["period"] == df["period"].max()].copy()
    return latest[geo_cols + [
        "digital_inclusion_index",
        "migration_intensity_score",
        "service_stress_index",
        "data_quality_friction_index",
        "biometric_failure_risk_score",
    ]]


def plot_top(df, geo_cols, metric, n=10, title=""):
    cols = geo_cols + [metric]
    top = df[cols].sort_values(metric, ascending=False).head(n)
    label_col = geo_cols[-1]
    plt.figure(figsize=(10, 6))
    sns.barplot(y=label_col, x=metric, data=top, palette="viridis")
    plt.title(title or f"Top {n} by {metric}")
    plt.tight_layout()
    outfile = PLOTS_DIR / f"top_{metric}_{label_col}.png"
    plt.savefig(outfile, dpi=200)
    plt.close()
    return outfile


def main():
    # State-level
    state_metrics = ROOT / "data" / "processed" / "metrics_state_M.parquet"
    if state_metrics.exists():
        df_state = load_latest(state_metrics, ["state"])
        for metric in [
            "digital_inclusion_index",
            "migration_intensity_score",
            "service_stress_index",
            "data_quality_friction_index",
            "biometric_failure_risk_score",
        ]:
            plot_top(df_state, ["state"], metric, n=10, title=f"State: Top 10 {metric}")

    # District-level
    district_metrics = ROOT / "data" / "processed" / "metrics_district_M.parquet"
    if district_metrics.exists():
        df_district = load_latest(district_metrics, ["state", "district"])
        for metric in [
            "digital_inclusion_index",
            "migration_intensity_score",
            "service_stress_index",
            "data_quality_friction_index",
            "biometric_failure_risk_score",
        ]:
            plot_top(df_district, ["state", "district"], metric, n=10, title=f"District: Top 10 {metric}")


if __name__ == "__main__":
    main()
