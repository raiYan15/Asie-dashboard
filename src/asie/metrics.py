from __future__ import annotations

from typing import Iterable, List

import numpy as np
import pandas as pd


def _pct_rank(series: pd.Series) -> pd.Series:
    return series.rank(pct=True).fillna(0.0)


def _safe_div(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    with np.errstate(divide="ignore", invalid="ignore"):
        out = numerator / denominator
    return out.replace([np.inf, -np.inf], 0.0).fillna(0.0)


def _group_pct_change(df: pd.DataFrame, keys: List[str], col: str) -> pd.Series:
    return df.sort_values(keys + ["period"]).groupby(keys)[col].pct_change().fillna(0.0)


def _group_positive_diff(df: pd.DataFrame, keys: List[str], col: str) -> pd.Series:
    return (
        df.sort_values(keys + ["period"])
        .groupby(keys)[col]
        .diff()
        .fillna(0.0)
        .clip(lower=0)
    )


def compute_indices(enrol: pd.DataFrame, demo: pd.DataFrame, bio: pd.DataFrame) -> pd.DataFrame:
    """Combine enrolment, demographic, and biometric aggregates into indices."""

    key_cols = [c for c in enrol.columns if c not in {"age_0_5", "age_5_17", "age_18_greater", "enrol_total"}]
    value_cols = [c for c in enrol.columns if c.startswith("age_")] + ["enrol_total"]

    combined = enrol.merge(demo, on=key_cols, how="outer", suffixes=("", "_demo"))
    combined = combined.merge(bio, on=key_cols, how="outer", suffixes=("", "_bio"))
    combined = combined.fillna(0)

    # Standard totals
    combined["enrol_total"] = combined.get("enrol_total", 0)
    combined["demo_total"] = combined.get("demo_total", 0)
    combined["bio_total"] = combined.get("bio_total", 0)

    combined["demo_to_enrol"] = _safe_div(combined["demo_total"], combined["enrol_total"])
    combined["bio_to_enrol"] = _safe_div(combined["bio_total"], combined["enrol_total"])

    # Lifecycle signals
    combined["youth_enrol_share"] = _safe_div(
        combined.get("age_0_5", 0) + combined.get("age_5_17", 0), combined["enrol_total"]
    )
    combined["adult_enrol_share"] = _safe_div(combined.get("age_18_greater", 0), combined["enrol_total"])
    combined["youth_bio_share"] = _safe_div(combined.get("bio_age_5_17", 0), combined["bio_total"])
    combined["adult_bio_share"] = _safe_div(combined.get("bio_age_17_plus", 0), combined["bio_total"])

    # Momentum terms (month-on-month growth and positive diffs)
    group_keys = [c for c in key_cols if c != "period"]
    combined = combined.sort_values(["period", *group_keys])
    combined["demo_mom"] = _group_pct_change(combined, group_keys, "demo_total")
    combined["demo_positive_diff"] = _group_positive_diff(combined, group_keys, "demo_total")
    combined["tx_load"] = combined["enrol_total"] + combined["demo_total"] + combined["bio_total"]

    # Digital Inclusion Index (DII)
    dii = (
        0.4 * _pct_rank(combined["enrol_total"])
        + 0.4 * _pct_rank(combined["demo_total"])
        + 0.2 * _pct_rank(combined["demo_to_enrol"])
    )
    combined["digital_inclusion_index"] = (dii * 100).round(2)

    # Migration Intensity Score (MIS)
    mis = 0.6 * _pct_rank(combined["demo_to_enrol"]) + 0.4 * _pct_rank(combined["demo_positive_diff"])
    combined["migration_intensity_score"] = (mis * 100).round(2)

    # Aadhaar Service Stress Index (ASSI)
    load_rank = _pct_rank(combined["tx_load"])
    spike_signal = _pct_rank(combined.groupby(group_keys)["tx_load"].transform(lambda s: (s - s.mean()) / (s.std(ddof=0) + 1e-9)))
    assi = 0.7 * load_rank + 0.3 * spike_signal
    combined["service_stress_index"] = (assi * 100).round(2)

    # Data Quality & Friction Index (DQFI) – higher implies more friction
    rework_ratio = _safe_div(combined["demo_total"] + combined["bio_total"], combined["enrol_total"].replace(0, np.nan))
    variability = combined.groupby(group_keys)["demo_total"].transform(lambda s: _safe_div(s.rolling(3, min_periods=1).std(), s.rolling(3, min_periods=1).mean() + 1e-9))
    dqfi = 0.6 * _pct_rank(rework_ratio.fillna(0)) + 0.4 * _pct_rank(variability.fillna(0))
    combined["data_quality_friction_index"] = (dqfi * 100).round(2)

    # Biometric Failure Risk Score (BFRS)
    bfrs = 0.6 * _pct_rank(combined["youth_bio_share"]) + 0.4 * _pct_rank(combined["bio_to_enrol"])
    combined["biometric_failure_risk_score"] = (bfrs * 100).round(2)

    return combined
