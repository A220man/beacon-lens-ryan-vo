import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { projectsApi, Project } from '../api/client'

export function ProjectDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [project, setProject] = useState<Project | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    setLoading(true)
    projectsApi.get(Number(id!))
      .then(setProject)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [id])

  const handleDelete = async () => {
    if (!window.confirm('Delete this project? This cannot be undone.')) return
    setDeleting(true)
    try {
      await projectsApi.delete(Number(id!))
      navigate('/projects')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to delete')
    } finally {
      setDeleting(false)
    }
  }

  if (loading) return <div className="card" style={{ textAlign: 'center' }}><div className="loading-spinner" /></div>
  if (error) return <div className="card" style={{ textAlign: 'center', color: 'var(--color-error)' }}>{error}</div>
  if (!project) return <div className="card empty-state"><h3>Project not found</h3><Link to="/projects" className="btn btn-primary" style={{ marginTop: '16px' }}>Back to Projects</Link></div>

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <Link to="/projects" className="btn btn-ghost" style={{ marginBottom: '8px', display: 'inline-block' }}>← Back</Link>
          <h1 style={{ fontSize: '32px', fontWeight: 700 }}>{project.name}</h1>
          <span className={`badge ${project.status === 'active' ? 'badge-success' : project.status === 'archived' ? 'badge-neutral' : 'badge-warning'}`} style={{ marginLeft: '12px' }}>{project.status}</span>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <Link to={`/projects/${project.id}/edit`} className="btn btn-secondary">Edit</Link>
          <button className="btn btn-ghost" style={{ color: 'var(--color-error)' }} onClick={handleDelete} disabled={deleting}>
            {deleting ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
        <div className="card">
          <h2 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '16px', color: 'var(--color-text-muted)' }}>Description</h2>
          {project.description ? (
            <p style={{ whiteSpace: 'pre-wrap' }}>{project.description}</p>
          ) : (
            <p style={{ color: 'var(--color-text-muted)' }}>No description provided.</p>
          )}
        </div>

        <div className="card">
          <h2 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '16px', color: 'var(--color-text-muted)' }}>ComfyUI Configuration</h2>
          {project.comfyui_url ? (
            <>
              <p><strong>URL:</strong> <code style={{ background: 'var(--color-bg)', padding: '2px 6px', borderRadius: 'var(--radius-sm)' }}>{project.comfyui_url}</code></p>
              {project.comfyui_workflow && (
                <details style={{ marginTop: '12px' }}>
                  <summary style={{ cursor: 'pointer', color: 'var(--color-primary)' }}>Workflow JSON</summary>
                  <pre style={{ marginTop: '8px', background: 'var(--color-bg)', padding: '12px', borderRadius: 'var(--radius-md)', overflow: 'auto', fontSize: '12px', maxHeight: '300px' }}>{project.comfyui_workflow}</pre>
                </details>
              )}
            </>
          ) : (
            <p style={{ color: 'var(--color-text-muted)' }}>No ComfyUI configuration set.</p>
          )}
        </div>

        <div className="card" style={{ gridColumn: '1 / -1' }}>
          <h2 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '16px', color: 'var(--color-text-muted)' }}>Metadata</h2>
          <dl style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
            <div><dt style={{ fontSize: '12px', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>Created</dt><dd style={{ fontFamily: 'monospace' }}>{new Date(project.created_at).toLocaleString()}</dd></div>
            <div><dt style={{ fontSize: '12px', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>Updated</dt><dd style={{ fontFamily: 'monospace' }}>{new Date(project.updated_at).toLocaleString()}</dd></div>
            <div><dt style={{ fontSize: '12px', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>ID</dt><dd style={{ fontFamily: 'monospace' }}>{project.id}</dd></div>
          </dl>
        </div>

        <div className="card" style={{ gridColumn: '1 / -1' }}>
          <h2 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '16px', color: 'var(--color-text-muted)' }}>Quick Actions</h2>
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <button className="btn btn-primary" disabled={!project.comfyui_url}>
              <span className="loading-spinner" style={{ width: '16px', height: '16px', display: 'none' }} />
              Generate Storyboard
            </button>
            <button className="btn btn-secondary" disabled={!project.comfyui_url}>
              Test ComfyUI Connection
            </button>
            <span style={{ display: 'flex', alignItems: 'center', color: 'var(--color-text-muted)', fontSize: '14px' }}>
              {project.comfyui_url ? 'ComfyUI configured' : 'Configure ComfyUI URL to enable generation'}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}