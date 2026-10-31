import { api } from '../../lib/api'

export interface Note {
  id: number
  title: string
  body: string
  /** sent back on every update, so the server can tell when someone else saved first */
  version: number
  updatedAt: string
}

export interface NotePage {
  content: Note[]
  page: { size: number; number: number; totalElements: number; totalPages: number }
}

export interface SaveNote {
  title: string
  body: string
  version?: number
}

/** Query keys in one place, as a hierarchy: invalidating ['notes', 'list'] refreshes every list, not the details. */
export const noteKeys = {
  all: ['notes'] as const,
  lists: () => [...noteKeys.all, 'list'] as const,
  list: (q: string, page: number) => [...noteKeys.lists(), { q, page }] as const,
  detail: (id: number) => [...noteKeys.all, 'detail', id] as const,
}

export const PAGE_SIZE = 10

export const notesApi = {
  list: (q: string, page: number, signal?: AbortSignal) =>
    api.get<NotePage>(`/notes?q=${encodeURIComponent(q)}&page=${page}&size=${PAGE_SIZE}`, { signal }),
  get: (id: number, signal?: AbortSignal) => api.get<Note>(`/notes/${id}`, { signal }),
  create: (body: SaveNote) => api.post<Note>('/notes', body),
  update: (id: number, body: SaveNote) => api.put<Note>(`/notes/${id}`, body),
  remove: (id: number) => api.del<void>(`/notes/${id}`),
}
