# ASIE Dashboard - Quick Start Guide

## 🎯 What's Fixed

| Issue | Status | Evidence |
|-------|--------|----------|
| 1️⃣ State Dropdown Broken | ✅ FIXED | All 36 states load from `/api/geo/states` |
| 2️⃣ Data Not Loading | ✅ FIXED | API routes now have `/api` prefix |
| 3️⃣ Metric Buttons Inactive | ✅ FIXED | Global state drives all panels |
| 4️⃣ Time-Series Empty | ✅ FIXED | Renders with data + 6-month forecast |
| 5️⃣ Anomaly Panel Static | ✅ FIXED | Fully data-driven with severity tags |

---

## 🚀 Start Here

### Backend (Port 8000)
```bash
python -m uvicorn api.main:app --reload --port 8000
```
✅ Should show: `Uvicorn running on http://127.0.0.1:8000`

### Frontend (Port 5174)
```bash
cd dashboard
npm run dev
```
✅ Should show: `Local: http://localhost:5174/`

### Open Dashboard
```
http://localhost:5174
```

---

## ✨ Try These

### 1. State Selection
1. Look at **Time-Series panel** (left)
2. See state dropdown
3. Select **"Andhra Pradesh"** or **"Maharashtra"**
4. Chart updates instantly ✅

### 2. Metric Switching
1. Look at **metric buttons** (top right)
2. Click **"Migration Intensity Score"**
3. Everything updates:
   - KPI values change
   - Charts re-render
   - Anomalies refetch ✅

### 3. Anomalies
1. Scroll down to **Anomaly panel** (right)
2. See real anomaly data
3. Look for **severity badges** (Low/Medium/High)
4. Try state filter dropdown ✅

### 4. Forecast
1. Look at **Time-Series chart**
2. See solid blue line (history)
3. See dotted orange line (forecast 6 months)
4. Notice trend arrow (↑ ↓ →) ✅

---

## 📊 What You'll See

### Header
```
ASIE – Aadhaar Societal Intelligence Engine
Governance Analytics | UIDAI | Aggregated & Privacy-Safe
Latest data: 2025-12 • Update frequency: monthly
```

### KPI Grid
```
Digital Inclusion Index          Migration Intensity Score
95.61 (Top: Uttar Pradesh)       89.42 (Top: Delhi)
Period: 2025-12                  Period: 2025-12
```

### Time-Series
```
State: [Dropdown with all 36 states ✓]
District: [Optional dropdown]
[Line chart with history + forecast]
↑ Upward trend
```

### Top-10 Charts
```
1. Uttar Pradesh - 95.61
2. Delhi - 92.35
3. Maharashtra - 88.72
...
10. ...
```

### Anomalies
```
Period | Metric | State | Severity
2025-12 | digital_inclusion_index | Goa | 🔴 High
2025-11 | service_stress_index | Bihar | 🟡 Medium
```

---

## 🔍 How Data Flows

```
User clicks state dropdown
  ↓
Frontend calls GET /api/geo/states
  ↓
Backend returns all 36 states
  ↓
Dropdown populates dynamically
  ↓
User selects state
  ↓
useQuery re-fetches time-series
  ↓
Chart renders with new data
  ↓
User sees instant update ✅
```

---

## 🐛 If Something Doesn't Work

### Symptom: State dropdown empty
**Check:** Backend is running
```bash
# In new terminal
python -m uvicorn api.main:app --reload --port 8000
```

### Symptom: Charts showing "No data"
**Check:** API connection works
```powershell
# In PowerShell
(Invoke-WebRequest 'http://127.0.0.1:8000/api/meta' -UseBasicParsing).Content
# Should show JSON with periods, indices
```

### Symptom: Clicking metric buttons does nothing
**Check:** Console for errors
```javascript
// Press F12 → Console tab
// Look for red errors
// Look for [API] logs
```

### Symptom: Frontend won't load
**Check:** Port 5174 is not blocked
```bash
# Kill any process on 5174
# Restart Vite:
cd dashboard
npm run dev
```

---

## 📱 Key Features

✅ **Dynamic State Selection**
- All 36 states/UTs loaded from database
- Fast filtering and selection
- Instant chart updates

✅ **5 Metrics Available**
- Digital Inclusion Index
- Migration Intensity Score
- Service Stress Index
- Data Quality & Friction Index
- Biometric Failure Risk Score

✅ **Time-Series Visualization**
- Historical data (solid line)
- 6-month forecast (dotted line)
- Trend indicators (↑ ↓ →)
- Confidence bands

✅ **Anomaly Detection**
- Real anomalies from ML model
- Severity classification (Low/Medium/High)
- State & metric filtering
- Trending view

✅ **Top-10 Rankings**
- States ranked by metric
- Districts ranked by metric
- Month-over-month deltas
- Clear visualization

---

## 🎯 Success Indicators

You'll know it's working when:

1. ✅ Dashboard loads without errors
2. ✅ Header says "ASIE – Aadhaar Societal Intelligence Engine"
3. ✅ 5 metric buttons visible and clickable
4. ✅ KPI grid shows values (not "—")
5. ✅ State dropdown has 36+ states
6. ✅ Selecting state updates time-series
7. ✅ Chart shows both history (solid) and forecast (dotted)
8. ✅ Anomaly list has severity badges
9. ✅ Clicking metric buttons updates everything
10. ✅ No red errors in console (F12)

**If all 10 are ✅: PERFECT!**

---

## 📈 API Status

| Endpoint | Method | Status |
|----------|--------|--------|
| `/api/meta` | GET | ✅ Working |
| `/api/geo/states` | GET | ✅ Working |
| `/api/state/summary` | GET | ✅ Working |
| `/api/timeseries` | GET | ✅ Working |
| `/api/anomalies` | GET | ✅ Working |

---

## 🎓 Pro Tips

1. **To debug:** Open F12 console, filter by [API] logs
2. **To restart:** Ctrl+C both servers, then restart
3. **To change state:** Just click dropdown, change, charts update instantly
4. **To switch metric:** Click button, everything re-fetches automatically
5. **To see code:** Check `api/main.py` for routes, `dashboard/src/` for React

---

## 🏆 You're All Set!

The dashboard is fully functional. All data flows correctly from backend to frontend.

**Enjoy analyzing Aadhaar system performance!**

---

**Dashboard URL:** http://localhost:5174
**API URL:** http://127.0.0.1:8000
**Status:** 🟢 **LIVE & OPERATIONAL**
