import { Navigate, Outlet, useLocation } from 'react-router'
import { useMe } from './useMe'

/**
 * Keeps signed-out visitors away from the app screens.
 * This is only for a better experience: every API call is checked by the server again.
 */
export function RequireAuth() {
  const me = useMe()
  const location = useLocation()

  if (me.isPending) return <p className="status" role="status">Loading…</p>
  if (me.isError) {
    return (
      <p className="status" role="alert">
        Could not reach the server. <button onClick={() => me.refetch()}>Try again</button>
      </p>
    )
  }
  if (!me.data) {
    return <Navigate to="/login" replace state={{ from: location.pathname + location.search }} />
  }
  return <Outlet />
}
