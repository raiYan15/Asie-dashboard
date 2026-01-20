from __future__ import annotations

import numpy as np
import pandas as pd


def detect_anomalies(
    df: pd.DataFrame,
    value_cols: list[str],
    group_keys: list[str],
    threshold: float = 3.0,
) -> pd.DataFrame:
    """Detect z-score based anomalies per group for given value columns."""
    if "period" not in df.columns:
        raise ValueError("period column required for anomaly detection")

    df_sorted = df.sort_values([*group_keys, "period"])
    anomalies = []

    for col in value_cols:
        def _zs(group: pd.Series) -> pd.Series:
            mean = group.mean()
            std = group.std(ddof=0) or 1e-9
            return (group - mean) / std

        zscores = df_sorted.groupby(group_keys)[col].transform(_zs)
        mask = zscores.abs() >= threshold
        flagged = df_sorted.loc[mask, ["period", *group_keys]].copy()
        flagged["metric"] = col
        flagged["zscore"] = zscores.loc[mask]
        flagged["direction"] = np.where(flagged["zscore"] > 0, "spike", "drop")
        anomalies.append(flagged)

    if not anomalies:
        return pd.DataFrame(columns=["period", *group_keys, "metric", "zscore", "direction"])

    return pd.concat(anomalies, ignore_index=True).sort_values(["period", "metric"])
