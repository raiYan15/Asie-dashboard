export function InsightStrip({ metric, stateSummary }) {
  const top = stateSummary?.[metric]?.[0]
  const second = stateSummary?.[metric]?.[1]
  if (!top) return null

  const metricName = metric.replace(/_/g, ' ')
  const delta = top[`${metric}_delta`] ?? top.delta
  const direction = delta > 0.5 ? 'rising' : delta < -0.5 ? 'easing' : 'stable'

  const narrative = ` ${top.state} leads in ${metricName} and is ${direction}. ${second ? `${second.state} follows closely.` : ''}`
  const recommendation = metric.includes('stress')
    ? 'Prioritise surge capacity, mobile enrolment, and queue management in hotspots.'
    : metric.includes('inclusion')
      ? 'Sustain outreach in high-performing states and replicate playbooks to lagging regions.'
      : metric.includes('biometric')
        ? 'Deploy fallback authentication, retraining, and device health checks in risk zones.'
        : 'Maintain vigilance and validate data pipelines for consistency.'

  return (
    <div className="insight-strip">
      <div>
        <p className="eyebrow">Strategic Insight</p>
        <h3>{top.state} spotlight</h3>
      </div>
      <p className="insight-text">{narrative} Recommended action: {recommendation}</p>
    </div>
  )
}
