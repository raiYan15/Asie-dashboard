from __future__ import annotations

from pathlib import Path
from typing import List

import pandas as pd

from . import anomalies, data_loader, metrics


DEFAULT_RAW = Path(__file__).resolve().parents[2] / "data" / "raw"
DEFAULT_PROCESSED = Path(__file__).resolve().parents[2] / "data" / "processed"
DEFAULT_REPORT = Path(__file__).resolve().parents[2] / "reports" / "summary.md"


def run_pipeline(
    geo_level: str = "state",
    freq: str = "M",
    raw_root: Path | str = DEFAULT_RAW,
    processed_root: Path | str = DEFAULT_PROCESSED,
    report_path: Path | str = DEFAULT_REPORT,
    anomaly_threshold: float = 3.0,
) -> None:
    raw_root = Path(raw_root)
    processed_root = Path(processed_root)
    processed_root.mkdir(parents=True, exist_ok=True)
    Path(report_path).parent.mkdir(parents=True, exist_ok=True)

    enrol = data_loader.load_enrolment(raw_root, freq=freq, geo_level=geo_level)
    demo = data_loader.load_demographic(raw_root, freq=freq, geo_level=geo_level)
    bio = data_loader.load_biometric(raw_root, freq=freq, geo_level=geo_level)

    combined = metrics.compute_indices(enrol, demo, bio)

    # Save processed datasets
    enrol.to_parquet(processed_root / f"enrolment_{geo_level}_{freq}.parquet", index=False)
    demo.to_parquet(processed_root / f"demographic_{geo_level}_{freq}.parquet", index=False)
    bio.to_parquet(processed_root / f"biometric_{geo_level}_{freq}.parquet", index=False)
    combined.to_parquet(processed_root / f"metrics_{geo_level}_{freq}.parquet", index=False)

    group_keys: List[str] = [c for c in combined.columns if c not in {"period", "enrol_total", "demo_total", "bio_total", "tx_load", "digital_inclusion_index", "migration_intensity_score", "service_stress_index", "data_quality_friction_index", "biometric_failure_risk_score"} and not c.endswith("share") and not c.endswith("ratio") and not c.endswith("index") and not c.endswith("score") and not c.endswith("_to_enrol") and not c.endswith("mom") and not c.endswith("diff")]
    if "period" in group_keys:
        group_keys.remove("period")

    anomaly_df = anomalies.detect_anomalies(
        combined,
        value_cols=["enrol_total", "demo_total", "bio_total", "tx_load"],
        group_keys=group_keys,
        threshold=anomaly_threshold,
    )
    anomaly_df.to_parquet(processed_root / f"anomalies_{geo_level}_{freq}.parquet", index=False)

    _write_summary(report_path, combined, anomaly_df, geo_level)


def _top_table(df: pd.DataFrame, column: str, n: int = 5) -> pd.DataFrame:
    cols = [c for c in df.columns if c not in {"period"} and not c.endswith("share") and not c.endswith("ratio") and not c.endswith("mom") and not c.endswith("diff")]
    geo_cols = [c for c in cols if c not in {
        column,
        "enrol_total",
        "demo_total",
        "bio_total",
        "tx_load",
        "digital_inclusion_index",
        "migration_intensity_score",
        "service_stress_index",
        "data_quality_friction_index",
        "biometric_failure_risk_score",
    }]
    geo_cols = [c for c in geo_cols if c != "period"]
    latest_period = df["period"].max()
    latest = df.loc[df["period"] == latest_period]
    return latest.sort_values(column, ascending=False)[[*geo_cols, column]].head(n)


def _write_summary(report_path: Path | str, combined: pd.DataFrame, anomaly_df: pd.DataFrame, geo_level: str) -> None:
    report_path = Path(report_path)
    latest_period = combined["period"].max()

    top_dii = _top_table(combined, "digital_inclusion_index")
    top_mis = _top_table(combined, "migration_intensity_score")
    top_assi = _top_table(combined, "service_stress_index")
    top_dqfi = _top_table(combined, "data_quality_friction_index")
    top_bfrs = _top_table(combined, "biometric_failure_risk_score")

    lines = [
        "# Aadhaar Societal Intelligence Engine (ASIE)\n",
        f"Geo level: **{geo_level}** | Frequency: **{latest_period.to_period('M')}**\n",
        "## Highlights (latest period)\n",
        f"- Top Digital Inclusion Index: {top_dii.to_dict(orient='records')}\n",
        f"- Top Migration Intensity Score: {top_mis.to_dict(orient='records')}\n",
        f"- Top Service Stress Index: {top_assi.to_dict(orient='records')}\n",
        f"- Highest Data Quality & Friction: {top_dqfi.to_dict(orient='records')}\n",
        f"- Highest Biometric Failure Risk: {top_bfrs.to_dict(orient='records')}\n",
        "\n## Anomalies\n",
    ]

    if anomaly_df.empty:
        lines.append("No anomalies detected with current threshold.\n")
    else:
        recent_anoms = anomaly_df.sort_values("period", ascending=False).head(20)
        lines.append(recent_anoms.to_markdown(index=False))
        lines.append("\n")

    lines.append("## Recommendations (state/district playbook)\n")
    lines.extend(
        [
            "- **Digital Inclusion (high DII leaders):** Consolidate gains with self-service + assisted channels; replicate playbook in mid-tier regions.\n",
            "- **Migration Intensity (high MIS):** Pre-position address/mobile update capacity; mobile camps in in-migration hotspots; multilingual comms.\n",
            "- **Service Stress (high ASSI):** Add temporary staff/slots, monitor kit uptime, triage complex cases to assisted counters.\n",
            "- **Data Friction (high DQFI):** Review exception codes/docs, simplify checklists, deploy senior resolver at centers with repeated rework.\n",
            "- **Biometric Risk (high BFRS):** Prioritize iris/face capture for youth/elderly; refresh/maintain devices; schedule proactive recapture drives.\n",
        ]
    )

    report_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    run_pipeline()
