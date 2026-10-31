import { QueryClientProvider } from '@tanstack/react-query'
import { render } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { createMemoryRouter, RouterProvider } from 'react-router'
import { createQueryClient } from '../lib/queryClient'
import { routes } from '../routes'
import { server } from './server'

export const asha = { id: 1, email: 'asha@example.com' }

/** The user is signed in: GET /api/me answers with them. */
export function signedIn(user = asha) {
  server.use(http.get('/api/me', () => HttpResponse.json(user)))
}

/** The user is signed out: GET /api/me answers 401, as it does without a cookie. */
export function signedOut() {
  server.use(http.get('/api/me', () => new HttpResponse(null, { status: 401 })))
}

export function note(id: number, overrides: Record<string, unknown> = {}) {
  return { id, title: `Note ${id}`, body: `Body ${id}`, version: 0, updatedAt: '2026-10-31T10:00:00Z', ...overrides }
}

export function pageOf(content: unknown[], totalPages = 1, number = 0) {
  return { content, page: { size: 10, number, totalElements: content.length, totalPages } }
}

/** The whole app, starting at a URL, with a fresh cache for every test. */
export function renderApp(route = '/notes') {
  const router = createMemoryRouter(routes, { initialEntries: [route] })
  const client = createQueryClient()
  client.setDefaultOptions({ queries: { retry: false, staleTime: 0 } })   // failure tests must not wait for retries
  const user = userEvent.setup()
  const result = render(
    <QueryClientProvider client={client}>
      <RouterProvider router={router} />
    </QueryClientProvider>,
  )
  return { user, router, client, ...result }
}
