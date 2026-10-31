import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { Link, useNavigate, useParams } from 'react-router'
import { z } from 'zod'
import { ApiError } from '../../lib/api'
import { showServerError } from '../../lib/forms'
import type { Note } from './notes.api'
import { useNote, useSaveNote } from './useNotes'

const schema = z.object({
  title: z.string().trim().min(1, 'Give the note a title').max(120, 'Keep the title under 120 characters'),
  body: z.string().max(5000, 'Keep the note under 5,000 characters'),
})
type Values = z.infer<typeof schema>

/** "/notes/new" has no id, and "/notes/:id" edits an existing note. */
export function NoteFormPage() {
  const { id } = useParams()
  if (id === undefined) return <NoteForm />
  const noteId = Number(id)
  if (!Number.isInteger(noteId) || noteId < 1) return <NotFound />
  return <EditNote id={noteId} />
}

function EditNote({ id }: { id: number }) {
  const note = useNote(id)

  if (note.isPending) return <p className="status" role="status">Loading note…</p>
  if (note.error instanceof ApiError && note.error.status === 404) return <NotFound />
  if (note.isError) {
    return (
      <p className="error" role="alert">
        Could not load this note. <button onClick={() => note.refetch()}>Try again</button>
      </p>
    )
  }
  // the key includes the version: after "load the latest", the form starts again from the server's copy
  return <NoteForm key={`${note.data.id}:${note.data.version}`} note={note.data} onReload={() => note.refetch()} />
}

function NotFound() {
  return (
    <section>
      <h1>Note not found</h1>
      <p>That note does not exist, or it belongs to someone else.</p>
      <Link to="/notes">Back to your notes</Link>
    </section>
  )
}

function NoteForm({ note, onReload }: { note?: Note; onReload?: () => unknown }) {
  const navigate = useNavigate()
  const save = useSaveNote()
  const {
    register,
    handleSubmit,
    setError,
    clearErrors,
    formState: { errors, isSubmitting, isDirty },
  } = useForm<Values>({
    resolver: zodResolver(schema),
    defaultValues: { title: note?.title ?? '', body: note?.body ?? '' },
  })
  const conflict = errors.root?.type === 'conflict'

  async function onSubmit(values: Values) {
    try {
      await save.mutateAsync({ id: note?.id, version: note?.version, ...values })
      navigate('/notes')
    } catch (e) {
      if (e instanceof ApiError && e.status === 409) {
        setError('root', { type: 'conflict', message: e.message })
      } else if (e instanceof ApiError && e.status === 404) {
        setError('root', { message: 'This note was deleted in the meantime.' })
      } else {
        showServerError(e, setError, 'Could not save. Please try again.')
      }
    }
  }

  return (
    <section>
      <h1>{note ? 'Edit note' : 'New note'}</h1>
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        {errors.root && (
          <div className="error" role="alert">
            <p>{errors.root.message}</p>
            {conflict && (
              <button type="button" onClick={() => { clearErrors('root'); void onReload?.() }}>
                Load the latest version (your changes here will be lost)
              </button>
            )}
          </div>
        )}

        <label htmlFor="title">Title</label>
        <input id="title" maxLength={200} aria-invalid={!!errors.title}
          aria-describedby={errors.title ? 'title-error' : undefined} {...register('title')} />
        {errors.title && <p className="error" id="title-error" role="alert">{errors.title.message}</p>}

        <label htmlFor="body">Text</label>
        <textarea id="body" rows={10} aria-invalid={!!errors.body}
          aria-describedby={errors.body ? 'body-error' : undefined} {...register('body')} />
        {errors.body && <p className="error" id="body-error" role="alert">{errors.body.message}</p>}

        <div className="actions">
          <button className="primary" disabled={isSubmitting || (!!note && !isDirty)}>
            {isSubmitting ? 'Saving…' : 'Save note'}
          </button>
          <Link to="/notes">Cancel</Link>
        </div>
      </form>
    </section>
  )
}
