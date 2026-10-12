import { useEffect, useState } from 'react'
import { healthApi } from '../api/client'

export function HealthBadge() {
  const [status, setStatus] = useState<'checking' | 'ok' | 'error'>('checking')

  useEffect(() => {
    healthApi.check()
      .then(() => setStatus('ok'))
      .catch(() => setStatus('error'))
  }, [])

  const config = {
    checking: { label: 'API…', className: 'badge-neutral' },
    ok: { label: 'API ✓', className: 'badge-success' },
    error: { label: 'API ✗', className: 'badge-error' },
  }[status]

  return <span className={`badge ${config.className}`}>{config.label}</span>
}