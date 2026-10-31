import { useMutation, useQueryClient } from '@tanstack/react-query'
import { NavLink, Outlet, useNavigate } from 'react-router'
import { meKey, useMe } from '../features/auth/useMe'
import { api } from '../lib/api'

export function Layout() {
  const me = useMe()
  const client = useQueryClient()
  const navigate = useNavigate()

  const logout = useMutation({
    mutationFn: () => api.post<void>('/auth/logout'),
    onSettled: () => {
      client.clear()                       // the next person on this computer must not see cached notes
      client.setQueryData(meKey, null)
      navigate('/login', { replace: true })
    },
  })

  return (
    <>
      <a className="skip" href="#main">Skip to content</a>
      <header className="topbar">
        <strong>Notes</strong>
        <nav aria-label="Main">
          <NavLink to="/notes">My notes</NavLink>
        </nav>
        <span className="spacer" />
        <span className="who">{me.data?.email}</span>
        <button onClick={() => logout.mutate()} disabled={logout.isPending}>Sign out</button>
      </header>
      <main id="main">
        <Outlet />
      </main>
    </>
  )
}
