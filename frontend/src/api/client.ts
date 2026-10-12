/// <reference types="vite/client" />

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  private async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${path}`
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }))
      throw new Error(error.detail || `HTTP ${response.status}`)
    }

    if (response.status === 204) {
      return undefined as T
    }

    return response.json()
  }

  get<T>(path: string) {
    return this.request<T>(path, { method: 'GET' })
  }

  post<T>(path: string, data: unknown) {
    return this.request<T>(path, { method: 'POST', body: JSON.stringify(data) })
  }

  patch<T>(path: string, data: unknown) {
    return this.request<T>(path, { method: 'PATCH', body: JSON.stringify(data) })
  }

  delete<T>(path: string) {
    return this.request<T>(path, { method: 'DELETE' })
  }
}

export const api = new ApiClient(API_BASE)

export interface Project {
  id: number
  name: string
  description: string | null
  status: 'draft' | 'active' | 'archived'
  comfyui_url: string | null
  comfyui_workflow: string | null
  created_at: string
  updated_at: string
}

export interface ProjectListResponse {
  items: Project[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface HealthResponse {
  status: string
  version: string
  environment: string
}

export const projectsApi = {
  list: (params?: { page?: number; page_size?: number; status?: string; search?: string }) => {
    const searchParams = new URLSearchParams()
    if (params?.page) searchParams.set('page', String(params.page))
    if (params?.page_size) searchParams.set('page_size', String(params.page_size))
    if (params?.status) searchParams.set('status', params.status)
    if (params?.search) searchParams.set('search', params.search)
    return api.get<ProjectListResponse>(`/api/v1/projects?${searchParams.toString()}`)
  },
  get: (id: number) => api.get<Project>(`/api/v1/projects/${id}`),
  create: (data: { name: string; description?: string; comfyui_url?: string; comfyui_workflow?: string }) =>
    api.post<Project>('/api/v1/projects', data),
  update: (id: number, data: Partial<Project>) => api.patch<Project>(`/api/v1/projects/${id}`, data),
  delete: (id: number) => api.delete<void>(`/api/v1/projects/${id}`),
}

export const healthApi = {
  check: () => api.get<HealthResponse>('/api/v1/health'),
}