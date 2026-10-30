import { Link } from 'react-router-dom'

export default function NotFound({ message = 'That page does not exist.' }) {
  return (
    <div className="mx-auto flex max-w-md flex-col items-center px-4 py-24 text-center">
      <h1 className="text-xl font-semibold">Not found</h1>
      <p className="mt-2 text-sm text-muted">{message}</p>
      <Link to="/" className="mt-5 rounded-lg border border-line px-3 py-1.5 text-sm text-muted hover:text-ink">
        Back to start
      </Link>
    </div>
  )
}
