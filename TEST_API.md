# ASIE Dashboard API & Frontend Integration Test

## ✅ Test Endpoints

### 1. Meta Information
```
GET http://127.0.0.1:8000/api/meta
Response: Latest period, frequency, has_district, indices
```

### 2. List All States
```
GET http://127.0.0.1:8000/api/geo/states
Response: { "states": [...] }
Expected: All 36 states/UTs in dropdown
```

### 3. State Summary (Top Metrics)
```
GET http://127.0.0.1:8000/api/state/summary
Response: For each index, top 10 states with scores and deltas
```

### 4. Time-Series for State
```
GET http://127.0.0.1:8000/api/timeseries?geo_level=state&state=Uttar%20Pradesh&metric=digital_inclusion_index
Response: Historical + forecast data
```

### 5. Anomalies
```
GET http://127.0.0.1:8000/api/anomalies?level=state&metric=digital_inclusion_index
Response: Anomalies with severity (Low/Medium/High)
```

## 🎯 Frontend Checklist

### State Dropdown
- [ ] Dropdown shows all states from API
- [ ] Can select different states
- [ ] Time-series updates when state changes

### Metric Buttons
- [ ] All 5 metric buttons visible and clickable
- [ ] Clicking updates all charts
- [ ] KPI values change per metric
- [ ] Anomaly panel shows correct metric

### Charts
- [ ] Time-series renders with historical data
- [ ] Forecast shows as dotted line (6 months ahead)
- [ ] Top-10 state bars display correctly
- [ ] Bars are ranked (1-10)

### Anomalies
- [ ] Shows/hides based on data
- [ ] State filter dropdown works
- [ ] Severity badges display (Low/Medium/High)
- [ ] Empty state message clear when no anomalies

### Error Handling
- [ ] Connection error if API is down
- [ ] Loading spinner while fetching
- [ ] Graceful recovery after error

## 🚀 Quick Manual Test

1. Open http://localhost:5174
2. Verify header shows "ASIE – Aadhaar Societal Intelligence Engine"
3. Check KPIs display top state for each metric
4. Click different metric buttons—all panels update
5. In Time-Series, select different state—chart updates
6. Scroll Anomaly table—see severity badges
7. Try state filter in Anomaly panel

## 🔧 Debug Commands

### Check API is serving
```powershell
(Invoke-WebRequest 'http://127.0.0.1:8000/api/meta' -UseBasicParsing).Content | ConvertFrom-Json
```

### Check frontend loads
```
Open browser console (F12)
Look for [API] logs
Check for errors in red
```

### Restart backend
```powershell
python -m uvicorn api.main:app --reload --port 8000
```

### Restart frontend
```powershell
cd dashboard
npm run dev
```
