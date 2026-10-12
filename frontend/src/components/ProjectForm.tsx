import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { projectsApi } from '../api/client'

export function ProjectForm() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const isEditing = Boolean(id)

  const [form, setForm] = useState({ name: '', description: '', status: 'draft' as 'draft' | 'active' | 'archived', comfyui_url: '', comfyui_workflow: '' })
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (isEditing) {
      setLoading(true)
      projectsApi.get(Number(id!))
        .then((data) => {
          setForm({ name: data.name, description: data.description || '', status: data.status, comfyui_url: data.comfyui_url || '', comfyui_workflow: data.comfyui_workflow || '' })
        })
        .catch((e) => setError(e.message))
        .finally(() => setLoading(false))
    }
  }, [id])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError(null)
    try {
      if (isEditing) {
        await projectsApi.update(Number(id!), form)
      } else {
        const created = await projectsApi.create(form)
        navigate(`/projects/${created.id}`)
        return
      }
      navigate(-1)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to save')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <div className="card" style={{ textAlign: 'center' }}><div className="loading-spinner" /></div>

  return (
    <div style={{ maxWidth: '700px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h1>{isEditing ? 'Edit Project' : 'New Project'}</h1>
        <Link to={isEditing ? `/projects/${id}` : '/projects'} className="btn btn-ghost">Cancel</Link>
      </div>

      <form onSubmit={handleSubmit} className="card" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {error && <div style={{ padding: '12px', backgroundColor: 'rgba(239,68,68,0.1)', border: '1px solid var(--color-error)', borderRadius: 'var(--radius-md)', color: 'var(--color-error)' }}>{error}</div>}

        <div>
          <label className="label">Name *</label>
          <input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required placeholder="Project name" />
        </div>

        <div>
          <label className="label">Description</label>
          <textarea className="input" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} rows={4} placeholder="Optional description..." />
        </div>

        <div>
          <label className="label">Status</label>
          <select className="input" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value as 'draft' | 'active' | 'archived' })}>
            <option value="draft">Draft</option>
            <option value="active">Active</option>
            <option value="archived">Archived</option>
          </select>
        </div>

        <div>
          <label className="label">ComfyUI URL</label>
          <input className="input" value={form.comfyui_url} onChange={(e) => setForm({ ...form, comfyui_url: e.target.value })} placeholder="http://localhost:8188" />
        </div>

        <div>
          <label className="label">ComfyUI Workflow (JSON)</label>
          <textarea className="input" value={form.comfyui_workflow} onChange={(e) => setForm({ ...form, comfyui_workflow: e.target.value })} rows={6} placeholder='Optional workflow JSON...' style={{ fontFamily: 'monospace', fontSize: '13px' }} />
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '8px' }}>
          <Link to={isEditing ? `/projects/${id}` : '/projects'} className="btn btn-secondary">Cancel</Link>
          <button type="submit" className="btn btn-primary" disabled={saving || !form.name.trim()}>
            {saving ? <><span className="loading-spinner" style={{ width: '16px', height: '16px' }} /> Saving...</> : (isEditing ? 'Save Changes' : 'Create Project')}
          </button>
        </div>
      </form>
    </div>
  )
}