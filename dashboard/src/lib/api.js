const API_BASE = (import.meta.env.VITE_API_URL?.replace(/\/$/, '') || 'https://asie-dashboard.onrender.com') + '/api'

export async function fetchJSON(path) {
  const fullUrl = path.startsWith('http') ? path : `${API_BASE}${path}`
  console.log('[API] Fetching:', fullUrl)
  try {
    const res = await fetch(fullUrl)
    if (!res.ok) {
      const text = await res.text()
      console.error('[API Error]', fullUrl, res.status, text)
      throw new Error(text || `Request failed: ${res.status}`)
    }
    const data = await res.json()
    console.log('[API Success]', fullUrl, data)
    return data
  } catch (err) {
    console.error('[API Exception]', fullUrl, err.message)
    throw err
  }
}

