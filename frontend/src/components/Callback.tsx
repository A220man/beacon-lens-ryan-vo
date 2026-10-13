import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { handleCallback } from '../auth/service'

export function Callback() {
  const navigate = useNavigate()

  useEffect(() => {
    handleCallback()
      .then(() => {
        navigate('/projects', { replace: true })
      })
      .catch((err) => {
        console.error('Authentication failed:', err)
        navigate(`/login?error=${encodeURIComponent(err.message)}`, { replace: true })
      })
  }, [navigate])

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
      <div className="card" style={{ textAlign: 'center', padding: '48px' }}>
        <div className="loading-spinner" style={{ margin: '0 auto 24px' }} />
        <h2>Completing sign-in...</h2>
        <p style={{ color: 'var(--color-text-muted)', marginTop: '12px' }}>
          Please wait while we finish logging you in.
        </p>
      </div>
    </div>
  )
}