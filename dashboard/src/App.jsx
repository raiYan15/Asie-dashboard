import { useQuery } from '@tanstack/react-query'
import { useMemo, useState, useEffect } from 'react'
import { KPIGrid } from './components/KPIGrid'
import { TopBarChart } from './components/TopBarChart'
import { AnomalyTable } from './components/AnomalyTable'
import { TimeSeries } from './components/TimeSeries'
import { InsightStrip } from './components/InsightStrip'
import { fetchJSON } from './lib/api.js'

const metrics = [
  { key: 'digital_inclusion_index', label: 'Digital Inclusion Index' },
  { key: 'migration_intensity_score', label: 'Migration Intensity Score' },
  { key: 'service_stress_index', label: 'Service Stress Index' },
  { key: 'data_quality_friction_index', label: 'Data Quality & Friction Index' },
  { key: 'biometric_failure_risk_score', label: 'Biometric Failure Risk Score' },
]

export default function App() {
  const [selectedMetric, setSelectedMetric] = useState(metrics[0].key)
  const { data: meta, isLoading: metaLoading, error: metaError } = useQuery({ queryKey: ['meta'], queryFn: () => fetchJSON('/meta') })
  const { data: stateSummary, isLoading: stateLoading, error: stateError } = useQuery({ queryKey: ['stateSummary', selectedMetric], queryFn: () => fetchJSON('/state/summary') })
  const { data: districtSummary, isLoading: districtLoading, error: districtError } = useQuery({ queryKey: ['districtSummary', selectedMetric], queryFn: () => fetchJSON('/district/summary'), enabled: !!meta?.has_district, retry: false })
  const { data: states, isLoading: statesLoading, error: statesError } = useQuery({ queryKey: ['states'], queryFn: () => fetchJSON('/geo/states'), retry: 2 })
  const [anomState, setAnomState] = useState('')
  const { data: anomalies, isLoading: anomLoading, error: anomError } = useQuery({ queryKey: ['anomalies', selectedMetric, anomState], queryFn: () => fetchJSON(`/anomalies?level=state&metric=${selectedMetric}${anomState ? `&state=${encodeURIComponent(anomState)}` : ''}`) })
  const [tsState, setTsState] = useState(states?.states?.[0] || 'Uttar Pradesh')
  const [tsDistrict, setTsDistrict] = useState(null)

  useEffect(() => {
    if (states?.states?.length && !states.states.includes(tsState)) {
      setTsState(states.states[0])
    }
  }, [states?.states])

  const kpis = useMemo(() => {
    if (!stateSummary) return []
    return metrics.map(m => {
      const data = stateSummary?.[m.key] ?? []
      return {
        label: m.label,
        value: data?.[0]?.[m.key] ?? '—',
        geo: data?.[0]?.state ?? '—'
      }
    })
  }, [stateSummary])

  if (metaError || stateError || statesError) {
    return (
      <div className="page">
        <div style={{ padding: '20px', color: '#b91c1c', background: '#fee2e2', borderRadius: '8px' }}>
          <h2>⚠️ Connection Error</h2>
          <p>Unable to fetch data from backend. Ensure API is running at http://127.0.0.1:8000</p>
          <p style={{ fontSize: '12px', color: '#7f1d1d' }}>
            {metaError?.message || stateError?.message || statesError?.message}
          </p>
        </div>
      </div>
    )
  }

  if (metaLoading || statesLoading) {
    return (
      <div className="page">
        <div style={{ padding: '20px', textAlign: 'center', color: '#64748b' }}>
          Loading dashboard...
        </div>
      </div>
    )
  }

  return (
    <div className="page">
      <header className="masthead">
        <div>
          <p className="eyebrow">Governance Analytics | UIDAI | Aggregated & Privacy-Safe</p>
          <h1>ASIE – Aadhaar Societal Intelligence Engine</h1>
          <p className="subtitle">Latest data: {meta?.latest_period ?? '…'} • Update frequency: {meta?.frequency ?? '—'}</p>
        </div>
        <div className="metric-picker" aria-label="Metric selector">
          {metrics.map(m => (
            <button key={m.key} className={selectedMetric === m.key ? 'active' : ''} onClick={() => setSelectedMetric(m.key)}>
              {m.label}
            </button>
          ))}
        </div>
      </header>

      <KPIGrid items={kpis} latestPeriod={stateSummary?.latest_period} />

      <section className="grid two">
        <TimeSeries
          metric={selectedMetric}
          geoLevel={tsDistrict ? 'district' : 'state'}
          stateName={tsState}
          districtName={tsDistrict}
          onGeoChange={(s, d) => { setTsState(s); setTsDistrict(d || null); }}
          states={states?.states}
        />
        <AnomalyTable data={anomalies?.rows} selectedMetric={selectedMetric} anomState={anomState} onStateChange={setAnomState} states={states?.states} />
      </section>

      <InsightStrip metric={selectedMetric} stateSummary={stateSummary} />

      <section className="grid two">
        <TopBarChart title={`States – ${metrics.find(m => m.key === selectedMetric)?.label}`} data={stateSummary?.[selectedMetric]} xKey={selectedMetric} yKey="state" />
        {districtSummary && (
          <TopBarChart title={`Districts – ${metrics.find(m => m.key === selectedMetric)?.label}`} data={districtSummary?.[selectedMetric]} xKey={selectedMetric} yKey="district" />
        )}
      </section>
    </div>
  )
}
