/** What Spring Boot sends for every error (RFC 9457 "problem details"). */
export interface Problem {
  title?: string
  detail?: string
  status?: number
  /** field name -> message, for validation failures */
  errors?: Record<string, string>
}

export class ApiError extends Error {
  status: number
  problem: Problem | null

  constructor(status: number, problem: Problem | null, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.problem = problem
  }

  get fieldErrors(): Record<string, string> {
    return this.problem?.errors ?? {}
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers)
  if (init.body !== undefined && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  let res: Response
  try {
    // same origin: the HttpOnly cookie travels automatically, and no token ever touches JavaScript
    res = await fetch(`/api${path}`, { ...init, headers })
  } catch (e) {
    if (e instanceof DOMException && e.name === 'AbortError') throw e
    throw new ApiError(0, null, 'Cannot reach the server. Check your connection and try again.')
  }

  if (!res.ok) {
    const problem = (await res.json().catch(() => null)) as Problem | null
    throw new ApiError(res.status, problem, problem?.detail ?? `Request failed (${res.status})`)
  }
  return res.status === 204 ? (undefined as T) : ((await res.json()) as T)
}

export const api = {
  get: <T>(path: string, init?: RequestInit) => request<T>(path, init),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: 'POST', body: body === undefined ? undefined : JSON.stringify(body) }),
  put: <T>(path: string, body: unknown) => request<T>(path, { method: 'PUT', body: JSON.stringify(body) }),
  del: <T>(path: string) => request<T>(path, { method: 'DELETE' }),
}
