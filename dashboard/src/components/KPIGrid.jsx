export function KPIGrid({ items, latestPeriod }) {
  return (
    <div className="kpi-grid">
      {items?.map((kpi, idx) => (
        <div className="kpi" key={idx}>
          <div className="kpi-label">{kpi.label}</div>
          <div className="kpi-value">{kpi.value}</div>
          <div className="kpi-geo">Top: {kpi.geo}</div>
          <div className="kpi-meta">Period: {latestPeriod ?? '—'}</div>
        </div>
      ))}
    </div>
  )
}
