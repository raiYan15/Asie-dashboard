export function AnomalyTable({ data, selectedMetric, anomState, onStateChange, states }) {
  return (
    <div className="card">
      <div className="card-head">
        <div>
          <p className="eyebrow">Anomaly & Risk Monitor</p>
          <h3>{selectedMetric.replace(/_/g, ' ')}</h3>
        </div>
        <label className="inline-select">
          Focus state
          <select value={anomState} onChange={e => onStateChange(e.target.value)}>
            <option value="">All</option>
            {states?.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </label>
      </div>
      {!data?.length && <div className="empty">No anomalies detected at the current threshold. System operating within expected limits.</div>}
      {data?.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Period</th>
              <th>Metric</th>
              <th>State</th>
              <th>District</th>
              <th>Direction</th>
              <th>Severity</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr key={idx}>
                <td>{row.period}</td>
                <td>{row.metric}</td>
                <td>{row.state ?? '—'}</td>
                <td>{row.district ?? '—'}</td>
                <td>{row.direction}</td>
                <td><span className={`pill ${row.severity?.toLowerCase()}`}>{row.severity}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
