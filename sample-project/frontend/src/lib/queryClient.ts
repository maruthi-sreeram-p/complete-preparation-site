import { QueryCache, QueryClient } from '@tanstack/react-query'
import { meKey } from '../features/auth/useMe'
import { ApiError } from './api'

export function createQueryClient() {
  const client: QueryClient = new QueryClient({
    queryCache: new QueryCache({
      onError: (error) => {
        // the token expired while the page was open: forget the user, and RequireAuth sends them to sign in
        if (error instanceof ApiError && error.status === 401) {
          client.setQueryData(meKey, null)
        }
      },
    }),
    defaultOptions: {
      queries: {
        staleTime: 30_000,
        // retrying a 4xx never helps, and makes a 404 look slow
        retry: (count, error) => !(error instanceof ApiError && error.status >= 400 && error.status < 500) && count < 2,
      },
    },
  })
  return client
}
