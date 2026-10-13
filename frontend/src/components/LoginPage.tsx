import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useAuth } from '../auth/context'
import { initiateLogin } from '../auth/service'

export function LoginPage() {
  const { isAuthenticated } = useAuth()
  const [searchParams] = useSearchParams()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const errorParam = searchParams.get('error')
    if (errorParam) {
      setError(errorParam)
    }
  }, [searchParams])

  useEffect(() => {
    if (isAuthenticated) {
      // Already logged in, redirect
      window.location.href = '/projects'
    }
  }, [isAuthenticated])

  const handleLogin = async () => {
    setError(null)
    try {
      await initiateLogin()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    }
  }

  return (
    <div style={{ maxWidth: '480px', margin: '0 auto', paddingTop: '80px' }}>
      <div className="card" style={{ padding: '48px', textAlign: 'center' }}>
        <h1 style={{ fontSize: '32px', fontWeight: 700, marginBottom: '8px' }}>beacon-lens</h1>
        <p style={{ color: 'var(--color-text-muted)', marginBottom: '32px' }}>
          Sign in to access your projects
        </p>

        {error && (
          <div
            style={{
              padding: '12px 16px',
              backgroundColor: 'rgba(239,68,68,0.1)',
              border: '1px solid var(--color-error)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--color-error)',
              marginBottom: '24px',
              textAlign: 'left',
            }}
          >
            {error}
          </div>
        )}

        <button
          onClick={handleLogin}
          className="btn btn-primary"
          style={{ width: '100%', padding: '14px 24px', fontSize: '16px' }}
        >
          <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z" />
              <path d="M2 12h20" />
              <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
            </svg>
            Sign in with Keycloak
          </span>
        </button>

        <p style={{ marginTop: '24px', color: 'var(--color-text-muted)', fontSize: '14px' }}>
          Demo mode: uses local Keycloak at <code>http://localhost:8080</code>
        </p>
      </div>
    </div>
  )
}