from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "processed"
PLOTS_DIR = ROOT / "reports" / "plots"

INDEX_COLUMNS = [
    "digital_inclusion_index",
    "migration_intensity_score",
    "service_stress_index",
    "data_quality_friction_index",
    "biometric_failure_risk_score",
]

app = FastAPI(title="ASIE Governance API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"]
)

if PLOTS_DIR.exists():
    app.mount("/charts", StaticFiles(directory=PLOTS_DIR), name="charts")


@lru_cache(maxsize=8)
def _load_parquet(name: str) -> pd.DataFrame:
    path = DATA_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Missing parquet: {path}")
    return pd.read_parquet(path)


def _load_forecast(name: str) -> Optional[pd.DataFrame]:
    path = DATA_DIR / name
    if not path.exists():
        return None
    df = pd.read_parquet(path)
    df["period"] = df["period"].dt.to_timestamp()
    return df


def _latest_period(df: pd.DataFrame) -> pd.Timestamp:
    return df["period"].max()


def _filter_latest(df: pd.DataFrame) -> pd.DataFrame:
    latest = _latest_period(df)
    return df[df["period"] == latest].copy()


def _top_n(df: pd.DataFrame, geo_cols: List[str], metric: str, n: int = 10) -> List[Dict]:
    delta_col = f"{metric}_delta"
    cols = geo_cols + [metric]
    if delta_col in df.columns:
        cols.append(delta_col)
    ranked = df[cols].sort_values(metric, ascending=False).head(n)
    ranked = ranked.reset_index(drop=True)
    ranked["rank"] = ranked.index + 1
    return ranked.to_dict(orient="records")


def _available_periods(df: pd.DataFrame) -> List[str]:
    return sorted(df["period"].dt.strftime("%Y-%m").unique().tolist())


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/meta")
def meta():
    state_df = _load_parquet("metrics_state_M.parquet")
    district_df = _load_parquet("metrics_district_M.parquet") if (DATA_DIR / "metrics_district_M.parquet").exists() else None
    return {
        "periods": _available_periods(state_df),
        "latest_period": _latest_period(state_df).strftime("%Y-%m"),
        "has_district": district_df is not None,
        "indices": INDEX_COLUMNS,
        "frequency": "monthly",
    }


@app.get("/api/geo/states")
def list_states():
    df = _load_parquet("metrics_state_M.parquet")
    states = sorted(df["state"].dropna().unique().tolist())
    return {"states": states}


@app.get("/api/geo/districts")
def list_districts(state: str = Query(...)):
    path = DATA_DIR / "metrics_district_M.parquet"
    if not path.exists():
        raise HTTPException(status_code=404, detail="District metrics not available")
    df = _load_parquet(path.name)
    df = df[df["state"].str.lower() == state.lower()]
    if df.empty:
        raise HTTPException(status_code=404, detail="No matching state")
    districts = sorted(df["district"].dropna().unique().tolist())
    return {"districts": districts}


@app.get("/api/state/summary")
def state_summary(top_n: int = Query(10, le=50)):
    df_all = _load_parquet("metrics_state_M.parquet")
    latest = _filter_latest(df_all)
    prev_period = (
        df_all[df_all["period"] < _latest_period(df_all)]
        .sort_values("period")
        .groupby("state")
        .last()
        .reset_index()
    )
    merged = latest.merge(prev_period[["state", *INDEX_COLUMNS]], on="state", how="left", suffixes=("", "_prev"))
    for metric in INDEX_COLUMNS:
        merged[f"{metric}_delta"] = merged[metric] - merged.get(f"{metric}_prev", 0)
    payload = {metric: _top_n(merged, ["state"], metric, n=top_n) for metric in INDEX_COLUMNS}
    return {"latest_period": _latest_period(df_all).strftime("%Y-%m"), **payload}


@app.get("/api/district/summary")
def district_summary(state: Optional[str] = None, top_n: int = Query(10, le=50)):
    path = DATA_DIR / "metrics_district_M.parquet"
    if not path.exists():
        raise HTTPException(status_code=404, detail="District metrics not available")
    df_all = _load_parquet(path.name)
    df = _filter_latest(df_all)
    if state:
        df = df[df["state"].str.lower() == state.lower()]
    if df.empty:
        raise HTTPException(status_code=404, detail="No matching districts")
    prev_period = df_all[df_all["period"] < _latest_period(df_all)]
    prev_period = (
        prev_period
        .sort_values("period")
        .groupby(["state", "district"])
        .last()
        .reset_index()
    )
    merged = df.merge(prev_period[["state", "district", *INDEX_COLUMNS]], on=["state", "district"], how="left", suffixes=("", "_prev"))
    for metric in INDEX_COLUMNS:
        merged[f"{metric}_delta"] = merged[metric] - merged.get(f"{metric}_prev", 0)
    df = merged
    payload = {metric: _top_n(df, ["state", "district"], metric, n=top_n) for metric in INDEX_COLUMNS}
    return {"latest_period": _latest_period(df).strftime("%Y-%m"), **payload}


@app.get("/api/timeseries")
def timeseries(
    geo_level: str = Query("state", pattern="^(state|district)$"),
    state: str = Query(...),
    district: Optional[str] = None,
    metric: str = Query(...),
    since: Optional[str] = None,
):
    file = "metrics_state_M.parquet" if geo_level == "state" else "metrics_district_M.parquet"
    df = _load_parquet(file)
    if metric not in df.columns:
        raise HTTPException(status_code=400, detail="Unknown metric")
    df = df[df["state"].str.lower() == state.lower()]
    if geo_level == "district":
        if not district:
            raise HTTPException(status_code=400, detail="district is required for district timeseries")
        df = df[df["district"].str.lower() == district.lower()]
    if since:
        try:
            since_ts = pd.Period(since).to_timestamp()
            df = df[df["period"] >= since_ts]
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid since format; use YYYY-MM")
    if df.empty:
        raise HTTPException(status_code=404, detail="No matching data")
    df = df.sort_values("period")
    resp = {
        "geo_level": geo_level,
        "state": state,
        "district": district,
        "metric": metric,
        "series": df["period"].dt.strftime("%Y-%m").tolist(),
        "values": df[metric].round(2).tolist(),
    }
    forecast_file = "forecast_state.parquet" if geo_level == "state" else "forecast_district.parquet"
    fc = _load_forecast(forecast_file)
    if fc is not None:
        fc_sel = fc[(fc["metric"] == metric) & (fc["state"].str.lower() == state.lower())]
        if geo_level == "district" and district:
            fc_sel = fc_sel[fc_sel["district"].str.lower() == district.lower()]
        if not fc_sel.empty:
            fc_sel = fc_sel.sort_values("period")
            resp["forecast_series"] = fc_sel["period"].dt.strftime("%Y-%m").tolist()
            resp["forecast_values"] = fc_sel["forecast"].tolist()
    return resp


@app.get("/api/anomalies")
def anomalies(
    level: str = Query("state", pattern="^(state|district)$"),
    metric: Optional[str] = None,
    since: Optional[str] = None,
    state: Optional[str] = None,
):
    file = "anomalies_state_M.parquet" if level == "state" else "anomalies_district_M.parquet"
    path = DATA_DIR / file
    if not path.exists():
        raise HTTPException(status_code=404, detail="Anomalies file not available")
    df = _load_parquet(path.name)
    if metric:
        df = df[df["metric"] == metric]
    if state:
        df = df[df["state"].str.lower() == state.lower()]
    if since:
        try:
            since_ts = pd.Period(since).to_timestamp()
            df = df[df["period"] >= since_ts]
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid since format; use YYYY-MM")
    if df.empty:
        return {"rows": []}
    def severity(z):
        az = abs(z)
        if az >= 3:
            return "High"
        if az >= 2.5:
            return "Medium"
        return "Low"

    df["severity"] = df["zscore"].apply(severity)
    df = df.sort_values(["period", "metric"], ascending=[False, True])
    df["period"] = df["period"].dt.strftime("%Y-%m")
    cols = [c for c in df.columns if c != "zscore"]
    return {"rows": df[cols].to_dict(orient="records")}


@app.get("/api/state/table")
def state_table(metric: str = Query(...), top_n: int = Query(20, le=100)):
    df = _filter_latest(_load_parquet("metrics_state_M.parquet"))
    if metric not in df.columns:
        raise HTTPException(status_code=400, detail="Unknown metric")
    return _top_n(df, ["state"], metric, n=top_n)


@app.get("/api/district/table")
def district_table(metric: str = Query(...), state: Optional[str] = None, top_n: int = Query(20, le=100)):
    path = DATA_DIR / "metrics_district_M.parquet"
    if not path.exists():
        raise HTTPException(status_code=404, detail="District metrics not available")
    df = _filter_latest(_load_parquet(path.name))
    if metric not in df.columns:
        raise HTTPException(status_code=400, detail="Unknown metric")
    if state:
        df = df[df["state"].str.lower() == state.lower()]
    if df.empty:
        raise HTTPException(status_code=404, detail="No matching data")
    return _top_n(df, ["state", "district"], metric, n=top_n)


# Entry point helper for uvicorn

def create_app():
    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
