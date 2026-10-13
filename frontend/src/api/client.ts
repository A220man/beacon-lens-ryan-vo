/// <reference types="vite/client" />

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

class ApiClient {
  private baseUrl: string
  private getAccessToken: () => Promise<string | null>

  constructor(baseUrl: string, getAccessToken: () => Promise<string | null>) {
    this.baseUrl = baseUrl
    this.getAccessToken = getAccessToken
  }

  private async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${path}`
    const accessToken = await this.getAccessToken()
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    }
    if (accessToken) {
      headers.Authorization = `Bearer ${accessToken}`
    }
    const response = await fetch(url, {
      headers,
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

let apiInstance: ApiClient | null = null

export function initApiClient(getAccessToken: () => Promise<string | null>) {
  apiInstance = new ApiClient(API_BASE, getAccessToken)
}

export function getApiClient(): ApiClient {
  if (!apiInstance) {
    throw new Error('API client not initialized. Call initApiClient first.')
  }
  return apiInstance
}

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
    return getApiClient().get<ProjectListResponse>(`/api/v1/projects?${searchParams.toString()}`)
  },
  get: (id: number) => getApiClient().get<Project>(`/api/v1/projects/${id}`),
  create: (data: { name: string; description?: string; comfyui_url?: string; comfyui_workflow?: string }) =>
    getApiClient().post<Project>('/api/v1/projects', data),
  update: (id: number, data: Partial<Project>) => getApiClient().patch<Project>(`/api/v1/projects/${id}`, data),
  delete: (id: number) => getApiClient().delete<void>(`/api/v1/projects/${id}`),
}

export const healthApi = {
  check: () => getApiClient().get<HealthResponse>('/api/v1/health'),
}