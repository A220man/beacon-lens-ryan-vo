import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { projectsApi, Project } from '../api/client'

export function ProjectList() {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [pagination, setPagination] = useState({ total: 0, page: 1, page_size: 20, total_pages: 0 })
  const [filters, setFilters] = useState({ status: '', search: '', page: 1 })

  const fetchProjects = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await projectsApi.list({ page: pagination.page, page_size: pagination.page_size, status: filters.status, search: filters.search })
      setProjects(data.items)
      setPagination(data)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load projects')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchProjects() }, [pagination.page, filters.status, filters.search])

  if (loading && projects.length === 0) {
    return <div className="card" style={{ textAlign: 'center' }}><div className="loading-spinner" /></div>
  }

  if (error) {
    return <div className="card" style={{ textAlign: 'center', color: 'var(--color-error)' }}>{error}</div>
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: 700 }}>Projects</h1>
        <Link to="/projects/new" className="btn btn-primary">New Project</Link>
      </div>

      <div className="card" style={{ marginBottom: '24px', display: 'flex', gap: '16px', flexWrap: 'wrap', alignItems: 'flex-end' }}>
        <div style={{ flex: 1, minWidth: '200px' }}>
          <label className="label">Search</label>
          <input
            className="input"
            placeholder="Search by name or description..."
            value={filters.search}
            onChange={(e) => setFilters({ ...filters, search: e.target.value, page: 1 })}
          />
        </div>
        <div style={{ minWidth: '180px' }}>
          <label className="label">Status</label>
          <select className="input" value={filters.status} onChange={(e) => setFilters({ ...filters, status: e.target.value })}>
            <option value="">All</option>
            <option value="draft">Draft</option>
            <option value="active">Active</option>
            <option value="archived">Archived</option>
          </select>
        </div>
      </div>

      {projects.length === 0 ? (
        <div className="card empty-state">
          <h3>No projects yet</h3>
          <p>Create your first project to get started.</p>
          <Link to="/projects/new" className="btn btn-primary" style={{ marginTop: '16px' }}>Create Project</Link>
        </div>
      ) : (
        <>
          <div className="card" style={{ overflow: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--color-border)', textAlign: 'left' }}>
                  <th style={{ padding: '12px 16px', fontWeight: 600, color: 'var(--color-text-muted)', fontSize: '13px', textTransform: 'uppercase' }}>Name</th>
                  <th style={{ padding: '12px 16px', fontWeight: 600, color: 'var(--color-text-muted)', fontSize: '13px', textTransform: 'uppercase' }}>Status</th>
                  <th style={{ padding: '12px 16px', fontWeight: 600, color: 'var(--color-text-muted)', fontSize: '13px', textTransform: 'uppercase' }}>Updated</th>
                  <th style={{ padding: '12px 16px', fontWeight: 600, color: 'var(--color-text-muted)', fontSize: '13px', textTransform: 'uppercase' }}></th>
                </tr>
              </thead>
              <tbody>
                {projects.map((p) => (
                  <tr key={p.id} style={{ borderBottom: '1px solid var(--color-border)' }}>
                    <td style={{ padding: '16px' }}>
                      <Link to={`/projects/${p.id}`} style={{ fontWeight: 500 }}>{p.name}</Link>
                      {p.description && <p style={{ fontSize: '13px', color: 'var(--color-text-muted)', marginTop: '4px', maxWidth: '400px', textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>{p.description}</p>}
                    </td>
                    <td style={{ padding: '16px' }}>
                      <span className={`badge ${p.status === 'active' ? 'badge-success' : p.status === 'archived' ? 'badge-neutral' : 'badge-warning'}`}>{p.status}</span>
                    </td>
                    <td style={{ padding: '16px', color: 'var(--color-text-muted)', fontSize: '14px' }}>
                      {new Date(p.updated_at).toLocaleDateString()}
                    </td>
                    <td style={{ padding: '16px', textAlign: 'right' }}>
                      <Link to={`/projects/${p.id}/edit`} className="btn btn-ghost btn-sm">Edit</Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {pagination.total_pages > 1 && (
            <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', marginTop: '16px' }}>
              <button className="btn btn-secondary" disabled={pagination.page === 1} onClick={() => setPagination({ ...pagination, page: pagination.page - 1 })}>
                Previous
              </button>
              <span style={{ display: 'flex', alignItems: 'center', color: 'var(--color-text-muted)' }}>
                Page {pagination.page} of {pagination.total_pages} ({pagination.total} total)
              </span>
              <button className="btn btn-secondary" disabled={pagination.page === pagination.total_pages} onClick={() => setPagination({ ...pagination, page: pagination.page + 1 })}>
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}