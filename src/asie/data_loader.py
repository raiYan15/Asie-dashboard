from __future__ import annotations

import glob
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

import pandas as pd

# Default date format in datasets
DATE_FMT = "%d-%m-%Y"


def _ensure_path(path: Path | str) -> Path:
    return Path(path).expanduser().resolve()


def _geo_cols_for_level(geo_level: str) -> List[str]:
    geo_level = geo_level.lower()
    if geo_level not in {"state", "district", "pincode"}:
        raise ValueError("geo_level must be one of: state, district, pincode")
    cols = ["state"]
    if geo_level in {"district", "pincode"}:
        cols.append("district")
    if geo_level == "pincode":
        cols.append("pincode")
    return cols


def _aggregate_chunk(
    chunk: pd.DataFrame,
    value_cols: Sequence[str],
    freq: str,
    geo_cols: Sequence[str],
) -> pd.DataFrame:
    # Parse and normalize date
    chunk["date"] = pd.to_datetime(chunk["date"], format=DATE_FMT, errors="coerce")
    chunk = chunk.dropna(subset=["date"])
    # Normalize pincode as string with leading zeros when present
    if "pincode" in chunk.columns:
        chunk["pincode"] = chunk["pincode"].astype(str).str.zfill(6)
    # Collapse to period
    chunk["period"] = chunk["date"].dt.to_period(freq).dt.to_timestamp()
    # Total across provided value columns
    chunk["total"] = chunk[value_cols].sum(axis=1)
    group_cols = ["period", *geo_cols]
    agg = (
        chunk.groupby(group_cols)[[*value_cols, "total"]]
        .sum(min_count=1)
        .reset_index()
    )
    return agg


def aggregate_csv_dir(
    csv_dir: Path | str,
    value_cols: Sequence[str],
    rename_map: Dict[str, str] | None = None,
    freq: str = "M",
    geo_level: str = "state",
    glob_pattern: str = "*.csv",
) -> pd.DataFrame:
    """Aggregate multiple CSVs in a directory by time period and geography.

    Parameters
    ----------
    csv_dir: directory containing CSV files
    value_cols: numeric columns to sum
    rename_map: optional column renames before aggregation
    freq: pandas period frequency string (e.g., "M" for monthly)
    geo_level: one of state|district|pincode
    glob_pattern: file pattern to match
    """

    base = _ensure_path(csv_dir)
    files = sorted(glob.glob(str(base / glob_pattern)))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {base}")

    geo_cols = _geo_cols_for_level(geo_level)
    frames: List[pd.DataFrame] = []

    for file in files:
        for chunk in pd.read_csv(
            file,
            chunksize=200_000,
            dtype={"state": "string", "district": "string", "pincode": "string"},
        ):
            if rename_map:
                chunk = chunk.rename(columns=rename_map)
            # keep only necessary columns
            needed_cols = ["date", *geo_cols, *value_cols]
            chunk = chunk[needed_cols]
            agg = _aggregate_chunk(chunk, value_cols=value_cols, freq=freq, geo_cols=geo_cols)
            frames.append(agg)

    if not frames:
        return pd.DataFrame(columns=["period", *geo_cols, *value_cols, "total"])

    combined = pd.concat(frames, ignore_index=True)
    grouped = combined.groupby(["period", *geo_cols]).sum(min_count=1).reset_index()
    return grouped


def load_enrolment(raw_root: Path | str, freq: str = "M", geo_level: str = "state") -> pd.DataFrame:
    base = _ensure_path(raw_root) / "enrolment" / "api_data_aadhar_enrolment"
    rename_map = {}
    value_cols = ["age_0_5", "age_5_17", "age_18_greater"]
    df = aggregate_csv_dir(base, value_cols=value_cols, rename_map=rename_map, freq=freq, geo_level=geo_level)
    df = df.rename(columns={"total": "enrol_total"})
    return df


def load_demographic(raw_root: Path | str, freq: str = "M", geo_level: str = "state") -> pd.DataFrame:
    base = _ensure_path(raw_root) / "demographic" / "api_data_aadhar_demographic"
    rename_map = {"demo_age_17_": "demo_age_17_plus"}
    value_cols = ["demo_age_5_17", "demo_age_17_plus"]
    df = aggregate_csv_dir(base, value_cols=value_cols, rename_map=rename_map, freq=freq, geo_level=geo_level)
    df = df.rename(columns={"total": "demo_total"})
    return df


def load_biometric(raw_root: Path | str, freq: str = "M", geo_level: str = "state") -> pd.DataFrame:
    base = _ensure_path(raw_root) / "biometric" / "api_data_aadhar_biometric"
    rename_map = {"bio_age_17_": "bio_age_17_plus"}
    value_cols = ["bio_age_5_17", "bio_age_17_plus"]
    df = aggregate_csv_dir(base, value_cols=value_cols, rename_map=rename_map, freq=freq, geo_level=geo_level)
    df = df.rename(columns={"total": "bio_total"})
    return df
