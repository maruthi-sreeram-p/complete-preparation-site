import { useQuery } from '@tanstack/react-query'
import { api, ApiError } from '../../lib/api'

export interface User {
  id: number
  email: string
}

export const meKey = ['me'] as const

/** The signed-in user, or null. The server's answer to GET /api/me is the single source of truth. */
export function useMe() {
  return useQuery({
    queryKey: meKey,
    queryFn: async ({ signal }) => {
      try {
        return await api.get<User>('/me', { signal })
      } catch (e) {
        if (e instanceof ApiError && e.status === 401) return null
        throw e
      }
    },
    retry: false,
    staleTime: 5 * 60_000,
  })
}
