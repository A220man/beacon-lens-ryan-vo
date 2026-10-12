/// <reference types="vitest/globals" />
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { ProjectList } from './ProjectList'
import { projectsApi } from '../api/client'

vi.mock('../api/client', () => ({
  projectsApi: {
    list: vi.fn(),
  },
  Project: {},
}))

const renderProjectList = () => render(<BrowserRouter><ProjectList /></BrowserRouter>)

describe('ProjectList', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    ;(projectsApi.list as vi.Mock).mockResolvedValue({
      items: [
        { id: 1, name: 'Project One', description: 'First', status: 'active', comfyui_url: null, comfyui_workflow: null, created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-02T00:00:00Z' },
        { id: 2, name: 'Project Two', description: 'Second', status: 'draft', comfyui_url: null, comfyui_workflow: null, created_at: '2024-01-03T00:00:00Z', updated_at: '2024-01-04T00:00:00Z' },
      ],
      total: 2,
      page: 1,
      page_size: 20,
      total_pages: 1,
    })
  })

  it('renders project list with data', async () => {
    renderProjectList()
    await waitFor(() => expect(screen.getByText('Project One')).toBeInTheDocument())
    expect(screen.getByText('Project Two')).toBeInTheDocument()
  })

  it('shows empty state when no projects', async () => {
    ;(projectsApi.list as vi.Mock).mockResolvedValueOnce({ items: [], total: 0, page: 1, page_size: 20, total_pages: 0 })
    renderProjectList()
    await waitFor(() => expect(screen.getByText('No projects yet')).toBeInTheDocument())
  })

  it('has link to create new project', async () => {
    renderProjectList()
    await waitFor(() => expect(screen.getByRole('link', { name: /new project/i })).toBeInTheDocument())
  })
})