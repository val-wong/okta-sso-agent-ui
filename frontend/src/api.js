export const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export async function apiGet(path, params = {}) {
  const url = new URL(path, API_BASE)
  Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v))
  const r = await fetch(url, { credentials: 'include' })
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}

export async function apiPost(path, data) {
  const url = new URL(path, API_BASE)
  const r = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
    credentials: 'include'
  })
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}

export function downloadText(filename, content) {
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}
