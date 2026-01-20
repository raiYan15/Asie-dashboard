import { useEffect, useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area } from 'recharts'
import { fetchJSON } from '../lib/api'

export function TimeSeries({ metric, stateName, districtName, onGeoChange, states }) {
  const [stateInput, setStateInput] = useState(stateName)
  const [districtInput, setDistrictInput] = useState(districtName || '')

  useEffect(() => {
    setStateInput(stateName)
    setDistrictInput(districtName || '')
  }, [stateName, districtName])

  useEffect(() => {
    if (states?.length) {
      const hasCurrent = states.includes(stateInput)
      if (!stateInput || !hasCurrent) {
        setStateInput(states[0])
        setDistrictInput('')
      }
    }
  }, [states])

  const geoLevel = districtInput ? 'district' : 'state'

  const { data: districtList, isLoading: distLoading } = useQuery({
    queryKey: ['districts', stateInput],
    queryFn: () => fetchJSON(`/geo/districts?state=${encodeURIComponent(stateInput)}`),
    enabled: !!stateInput,
  })

  const { data, isFetching, refetch, isError } = useQuery({
    queryKey: ['timeseries', geoLevel, metric, stateInput, districtInput],
    queryFn: () => {
      const url = `/timeseries?geo_level=${geoLevel}&state=${encodeURIComponent(stateInput)}${geoLevel === 'district' && districtInput ? `&district=${encodeURIComponent(districtInput)}` : ''}&metric=${metric}`
      console.log('[TimeSeries] Fetching:', url)
      return fetchJSON(url)
    },
    enabled: !!stateInput && !!metric,
    retry: 1,
  })

  const chartData = useMemo(() => {
    if (!data?.series) return []
    const base = data.series.map((p, i) => ({ period: p, value: data.values[i], kind: 'actual' }))
    const forecast = (data.forecast_series || []).map((p, i) => ({ period: p, forecast: data.forecast_values[i], kind: 'forecast' }))
    return [...base, ...forecast]
  }, [data])

  const direction = useMemo(() => {
    if (!data?.values?.length) return '→'
    const first = data.values[0]
    const last = data.values[data.values.length - 1]
    if (last > first * 1.01) return '↑'
    if (last < first * 0.99) return '↓'
    return '→'
  }, [data])

  return (
    <div className="card">
      <div className="card-head">
        <div>
          <p className="eyebrow">Time-Series Intelligence</p>
          <h3>{geoLevel === 'district' ? 'District trajectory' : 'State trajectory'} {direction}</h3>
        </div>
        <span className="pill">Forecast: 6 months</span>
      </div>
      <div className="ts-form">
        <label>
          State
          <select value={stateInput} onChange={e => { setStateInput(e.target.value); setDistrictInput(''); }}>
            {!stateInput && <option value="" disabled>Select a state</option>}
            {(states?.length ? states : stateInput ? [stateInput] : []).map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </label>
        <label>
          District (optional)
          <select value={districtInput} onChange={e => setDistrictInput(e.target.value)}>
            <option value="">All</option>
            {districtList?.districts?.map(d => <option key={d} value={d}>{d}</option>)}
          </select>
        </label>
        <button onClick={() => { onGeoChange(stateInput, districtInput || null); refetch(); }} disabled={isFetching}>
          {isFetching ? 'Loading…' : 'Update view'}
        </button>
      </div>
      {isError && <div className="empty">No data for the selection.</div>}
      <div style={{ width: '100%', height: 320 }}>
        <ResponsiveContainer>
          <LineChart data={chartData} margin={{ left: 12, right: 12 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="period" tick={{ fontSize: 10 }} angle={-20} height={50} />
            <YAxis width={60} />
            <Tooltip formatter={(val, key) => [val, key === 'forecast' ? 'Forecast' : 'Actual']} />
            <Line type="monotone" dataKey="value" stroke="#1d4ed8" strokeWidth={2} dot={false} name="Actual" />
            <Line type="monotone" dataKey="forecast" stroke="#ea580c" strokeWidth={2} strokeDasharray="4 2" dot={false} name="Forecast" />
            <Area type="monotone" dataKey="forecast" stroke="none" fill="#ea580c22" name="Forecast band" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
