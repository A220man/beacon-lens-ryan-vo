import { Routes, Route, Link, Navigate, useLocation } from 'react-router-dom'
import { AuthProvider, useAuth } from './auth/context'
import { initApiClient } from './api/client'
import { getValidAccessToken } from './auth/service'
import { HealthBadge } from './components/HealthBadge'
import { ProjectList } from './components/ProjectList'
import { ProjectForm } from './components/ProjectForm'
import { ProjectDetail } from './components/ProjectDetail'
import { Callback } from './components/Callback'
import { LoginPage } from './components/LoginPage'

initApiClient(getValidAccessToken)

function Layout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, logout, user } = useAuth()

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header style={{
        padding: '16px 24px',
        borderBottom: '1px solid var(--color-border)',
        backgroundColor: 'var(--color-bg-elevated)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        <Link to="/" style={{ fontSize: '20px', fontWeight: 700, color: 'var(--color-primary)', textDecoration: 'none' }}>
          beacon-lens
        </Link>
        <nav style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
          {isAuthenticated ? (
            <>
              <Link to="/projects" className="btn btn-ghost">Projects</Link>
              <Link to="/projects/new" className="btn btn-primary">New Project</Link>
              <span style={{ color: 'var(--color-text-muted)', fontSize: '14px', marginRight: '8px' }}>
                {user?.preferred_username || user?.email || 'User'}
              </span>
              <button onClick={logout} className="btn btn-secondary">Logout</button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-primary">Sign In</Link>
            </>
          )}
          <HealthBadge />
        </nav>
      </header>
      <main style={{ flex: 1, padding: '32px 24px' }}>
        <div className="container">{children}</div>
      </main>
      <footer style={{
        padding: '24px',
        borderTop: '1px solid var(--color-border)',
        textAlign: 'center',
        color: 'var(--color-text-muted)',
        fontSize: '14px',
      }}>
        beacon-lens v1.0.0 \u2014 Ryan Vo (ryandtvo@gmail.com)
      </footer>
    </div>
  )
}

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <div className="card" style={{ textAlign: 'center', padding: '48px' }}>
          <div className="loading-spinner" style={{ margin: '0 auto 24px' }} />
          <p>Verifying authentication...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return <>{children}</>
}

function Home() {
  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', textAlign: 'center' }}>
      <h1 style={{ fontSize: '48px', fontWeight: 700, marginBottom: '16px', background: 'linear-gradient(135deg, var(--color-primary), #a855f7)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
        beacon-lens
      </h1>
      <p style={{ fontSize: '20px', color: 'var(--color-text-muted)', marginBottom: '32px' }}>
        An intentional crafting engine for artists, designers, and filmmakers.
      </p>
      <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}>
        <Link to="/projects/new" className="btn btn-primary" style={{ padding: '14px 32px', fontSize: '16px' }}>
          Create Your First Project
        </Link>
        <Link to="/projects" className="btn btn-secondary" style={{ padding: '14px 32px', fontSize: '16px' }}>
          Browse Projects
        </Link>
      </div>
      <div style={{ marginTop: '64px', padding: '32px', backgroundColor: 'var(--color-bg-elevated)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)', textAlign: 'left' }}>
        <h2 style={{ marginBottom: '16px', fontSize: '20px' }}>Workflows</h2>
        <ul style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px', listStyle: 'none' }}>
          <li style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
            <span style={{ color: 'var(--color-primary)', fontSize: '20px' }}>🎬</span>
            <div>
              <strong>Script to Storyboard</strong><br/>
              <span style={{ color: 'var(--color-text-muted)', fontSize: '14px' }}>Parse Fountain scripts, generate AI storyboards via ComfyUI</span>
            </div>
          </li>
          <li style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
            <span style={{ color: 'var(--color-primary)', fontSize: '20px' }}>🖥️</span>
            <div>
              <strong>Local Generation</strong><br/>
              <span style={{ color: 'var(--color-text-muted)', fontSize: '14px' }}>Connect to your ComfyUI instance, no cloud required</span>
            </div>
          </li>
          <li style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
            <span style={{ color: 'var(--color-primary)', fontSize: '20px' }}>🐧</span>
            <div>
              <strong>Linux Native</strong><br/>
              <span style={{ color: 'var(--color-text-muted)', fontSize: '14px' }}>AppImage, DEB, RPM — runs anywhere</span>
            </div>
          </li>
        </ul>
      </div>
    </div>
  )
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/callback" element={<Callback />} />
      <Route
        path="/projects/*"
        element={
          <ProtectedRoute>
            <Routes>
              <Route path="/" element={<ProjectList />} />
              <Route path="new" element={<ProjectForm />} />
              <Route path=":id" element={<ProjectDetail />} />
              <Route path=":id/edit" element={<ProjectForm />} />
            </Routes>
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}

function App() {
  return (
    <AuthProvider>
      <Layout>
        <AppRoutes />
      </Layout>
    </AuthProvider>
  )
}

export default App