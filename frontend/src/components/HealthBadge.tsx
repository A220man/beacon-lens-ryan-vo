import { useEffect, useState, useCallback } from 'react'
import { healthApi } from '../api/client'

export function HealthBadge() {
  const [status, setStatus] = useState<'checking' | 'ok' | 'error'>('checking')

  const checkHealth = useCallback(async () => {
    try {
      await healthApi.check()
      setStatus('ok')
    } catch {
      setStatus('error')
    }
  }, [])

  useEffect(() => {
    // Defer the health check to avoid act() warnings in tests
    const timer = setTimeout(checkHealth, 0)
    return () => clearTimeout(timer)
  }, [checkHealth])

  const config = {
    checking: { label: 'API…', className: 'badge-neutral' },
    ok: { label: 'API ✓', className: 'badge-success' },
    error: { label: 'API ✗', className: 'badge-error' },
  }[status]

  return <span className={`badge ${config.className}`}>{config.label}</span>
}
