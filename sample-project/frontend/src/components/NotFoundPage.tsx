import { Link } from 'react-router'

export function NotFoundPage() {
  return (
    <main className="auth">
      <h1>Page not found</h1>
      <Link to="/notes">Go to your notes</Link>
    </main>
  )
}
