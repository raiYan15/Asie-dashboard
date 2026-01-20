# Aadhaar Societal Intelligence Engine (ASIE)

Policy-intelligence toolkit to turn aggregated Aadhaar enrolment and update data
into decision-ready insights (patterns, trends, anomalies, indices, and actions).

## What it does
- Ingests aggregated enrolment, demographic update, and biometric update CSVs.
- Aggregates to monthly periods at configurable geography levels (state/district/pincode).
- Builds composite indices: Digital Inclusion, Migration Intensity, Service Stress, Data Quality & Friction, Biometric Failure Risk.
- Flags anomalies via z-score spikes/drops.
- Emits Parquet datasets plus a concise Markdown summary.

## Getting started
1. Install deps (ideally inside a virtualenv):
   ```bash
   pip install -r requirements.txt
   ```
2. Run the pipeline (defaults: monthly, state-level):
   ```bash
   python -m scripts.run_pipeline
   ```
   - To switch geography granularity, edit `geo_level` in `scripts/run_pipeline.py`
     (choose from `state`, `district`, `pincode`).
3. Outputs land in `data/processed/`:
   - `enrolment_<geo>_M.parquet`
   - `demographic_<geo>_M.parquet`
   - `biometric_<geo>_M.parquet`
   - `metrics_<geo>_M.parquet` (all indices)
   - `anomalies_<geo>_M.parquet`
   - Summary report: `reports/summary.md`

4. Run the governance API (FastAPI):
   ```bash
   uvicorn api.main:app --reload --port 8000
   ```

5. Frontend dashboard (React + Vite):
   ```bash
   cd dashboard
   npm install
   npm run dev  # http://localhost:5173 (proxied to backend at 8000)
   ```

## Index formulas (scaled 0–100)
- **Digital Inclusion Index (DII):** 0.4 * rank(enrolment) + 0.4 * rank(demographic updates) + 0.2 * rank(demo-to-enrol ratio).
- **Migration Intensity Score (MIS):** 0.6 * rank(demo-to-enrol) + 0.4 * rank(positive growth in demographic updates).
- **Service Stress Index (ASSI):** 0.7 * rank(total load) + 0.3 * rank(load spike vs group mean/std).
- **Data Quality & Friction Index (DQFI):** 0.6 * rank(rework ratio: (demo+bio)/enrol) + 0.4 * rank(rolling variability of demographic updates). Higher = more friction.
- **Biometric Failure Risk Score (BFRS):** 0.6 * rank(youth biometric share) + 0.4 * rank(bio-to-enrol ratio). Higher = higher re-capture burden.

Notes:
- Ranks are percentile ranks computed over the full dataset; ratios are safeguarded against divide-by-zero.
- Formulas are transparent and easily tweakable in `src/asie/metrics.py`.

## Anomaly detection
- Z-score based, per geography group, default threshold = 3.0 on `enrol_total`, `demo_total`, `bio_total`, `tx_load`.
- You can override via `anomaly_threshold` in `run_pipeline` (e.g., scripts/run_pipeline uses 2.5 for higher sensitivity). For code-level tweaks, see `src/asie/anomalies.py`.

## Extending
- Switch `freq` in `scripts/run_pipeline.py` (e.g., `"W"` for weekly if data supports it).
- Add charts/dashboards by reading `metrics_*.parquet` into Plotly/Power BI/Metabase.
- Add population overlays or urban/rural flags to strengthen per-capita and inclusion signals.

## Caveats & ethics
- Data is aggregated and non-personal; no re-identification attempts.
- Indices are comparative within the provided dataset; add population/context data for absolute interpretation.
- Always pair automated findings with domain review before policy action.
