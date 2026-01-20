from __future__ import annotations

from pathlib import Path
from typing import List

import numpy as np
import pandas as pd


def _fit_linear_forecast(series: pd.Series, steps: int = 6) -> np.ndarray:
    """Simple linear regression forecast on index positions."""
    if len(series) < 3:
        return np.array([])
    x = np.arange(len(series))
    y = series.values
    slope, intercept = np.polyfit(x, y, 1)
    future_x = np.arange(len(series), len(series) + steps)
    return intercept + slope * future_x


def forecast_metrics(df: pd.DataFrame, geo_cols: List[str], metrics: List[str], periods_ahead: int = 6, min_history: int = 6) -> pd.DataFrame:
    rows = []
    df = df.sort_values([*geo_cols, "period"])
    latest_period = df["period"].max().to_period("M")
    for _, g in df.groupby(geo_cols):
        if len(g) < min_history:
            continue
        for metric in metrics:
            series = g[metric]
            forecast = _fit_linear_forecast(series, steps=periods_ahead)
            if forecast.size == 0:
                continue
            for step, value in enumerate(forecast, start=1):
                rows.append({
                    **{geo_cols[i]: g.iloc[0][geo_cols[i]] for i in range(len(geo_cols))},
                    "metric": metric,
                    "period": latest_period + step,
                    "forecast": float(round(value, 2)),
                })
    return pd.DataFrame(rows)


def run_forecasts(processed_root: Path | str, periods_ahead: int = 6) -> None:
    processed_root = Path(processed_root)
    state_path = processed_root / "metrics_state_M.parquet"
    district_path = processed_root / "metrics_district_M.parquet"
    metrics = [
        "enrol_total",
        "demo_total",
        "bio_total",
        "tx_load",
        "digital_inclusion_index",
        "migration_intensity_score",
        "service_stress_index",
        "data_quality_friction_index",
        "biometric_failure_risk_score",
    ]

    if state_path.exists():
        df = pd.read_parquet(state_path)
        fc = forecast_metrics(df, geo_cols=["state"], metrics=metrics, periods_ahead=periods_ahead)
        fc.to_parquet(processed_root / "forecast_state.parquet", index=False)

    if district_path.exists():
        df = pd.read_parquet(district_path)
        fc = forecast_metrics(df, geo_cols=["state", "district"], metrics=metrics, periods_ahead=periods_ahead)
        fc.to_parquet(processed_root / "forecast_district.parquet", index=False)