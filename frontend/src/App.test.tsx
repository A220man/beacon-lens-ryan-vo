/// <reference types="vitest/globals" />
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import App from './App'

const renderApp = () => render(<BrowserRouter><App /></BrowserRouter>)

describe('App', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    ;(global.fetch as vi.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ status: 'ok', version: '1.0.0', environment: 'development' }),
    })
  })

  it('renders beacon-lens title in header', () => {
    renderApp()
    expect(screen.getByRole('link', { name: 'beacon-lens' })).toBeInTheDocument()
  })

  it('shows health badge after API check', async () => {
    renderApp()
    await waitFor(() => expect(screen.getByText('API ✓')).toBeInTheDocument())
  })

  it('has Projects link in nav', async () => {
    renderApp()
    expect(screen.getByRole('link', { name: 'Projects' })).toBeInTheDocument()
  })

  it('renders workflow cards on home page', () => {
    renderApp()
    expect(screen.getByText('Script to Storyboard')).toBeInTheDocument()
    expect(screen.getByText('Local Generation')).toBeInTheDocument()
    expect(screen.getByText('Linux Native')).toBeInTheDocument()
  })
})