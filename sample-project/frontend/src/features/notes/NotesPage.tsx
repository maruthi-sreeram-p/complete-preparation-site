import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router'
import { useDebounce } from '../../lib/useDebounce'
import { useDeleteNote, useNotesList } from './useNotes'

const dateFormat = new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' })

export function NotesPage() {
  // search text and page live in the URL: links can be shared, refresh keeps the view, and Back works
  const [params, setParams] = useSearchParams()
  const q = params.get('q') ?? ''
  const page = Math.max(0, Number.parseInt(params.get('page') ?? '0', 10) || 0)

  // the input updates on every key, whereas the URL and the request wait for typing to pause
  const [draft, setDraft] = useState(q)
  const debounced = useDebounce(draft.trim(), 300)
  useEffect(() => {
    if (debounced !== q) setParams(debounced ? { q: debounced } : {}, { replace: true })
    // only when the debounced text changes: re-running on q would undo Back-button navigation
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debounced])

  const notes = useNotesList(q, page)
  const remove = useDeleteNote()
  const [confirming, setConfirming] = useState<number | null>(null)

  function goToPage(next: number) {
    const nextParams: Record<string, string> = {}
    if (q) nextParams.q = q
    if (next > 0) nextParams.page = String(next)
    setParams(nextParams)
  }

  const data = notes.data
  const totalPages = data?.page.totalPages ?? 0

  return (
    <section>
      <div className="toolbar">
        <h1>Your notes</h1>
        <Link className="button primary" to="/notes/new">New note</Link>
      </div>

      <label htmlFor="search">Search notes</label>
      <input id="search" type="search" value={draft} onChange={(e) => setDraft(e.target.value)} placeholder="Title or text" />

      {notes.isPending && <p className="status" role="status">Loading notes…</p>}

      {notes.isError && (
        <p className="error" role="alert">
          Could not load your notes. <button onClick={() => notes.refetch()}>Try again</button>
        </p>
      )}

      {remove.isError && <p className="error" role="alert">Could not delete that note. Please try again.</p>}

      {data && data.content.length === 0 && (
        <p className="empty">
          {q ? `No notes match “${q}”.` : 'No notes yet. Create your first one.'}
        </p>
      )}

      {data && data.content.length > 0 && (
        <ul className={`notes${notes.isPlaceholderData ? ' stale' : ''}`} aria-label="Notes">
          {data.content.map((note) => (
            <li key={note.id}>
              <div>
                <Link to={`/notes/${note.id}`}>{note.title}</Link>
                <p className="preview">{note.body.slice(0, 120) || 'No text'}</p>
                <p className="meta">Updated {dateFormat.format(new Date(note.updatedAt))}</p>
              </div>
              {confirming === note.id ? (
                <div className="confirm" role="group" aria-label={`Confirm deleting ${note.title}`}>
                  <span>Delete this note?</span>
                  <button className="danger" disabled={remove.isPending}
                    onClick={() => remove.mutate(note.id, { onSettled: () => setConfirming(null) })}>
                    Yes, delete
                  </button>
                  <button onClick={() => setConfirming(null)}>Keep it</button>
                </div>
              ) : (
                <button aria-label={`Delete ${note.title}`} onClick={() => { remove.reset(); setConfirming(note.id) }}>
                  Delete
                </button>
              )}
            </li>
          ))}
        </ul>
      )}

      {totalPages > 1 && (
        <nav className="pager" aria-label="Pagination">
          <button disabled={page === 0} onClick={() => goToPage(page - 1)}>Previous</button>
          <span>Page {page + 1} of {totalPages}</span>
          <button disabled={page + 1 >= totalPages} onClick={() => goToPage(page + 1)}>Next</button>
        </nav>
      )}
    </section>
  )
}
