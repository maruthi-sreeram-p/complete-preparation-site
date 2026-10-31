import { useState } from 'react'
import { ExternalLink, Plus, Trash2 } from 'lucide-react'
import { DoneToggle } from './QuestionCard.jsx'
import { usePractice } from './PracticeProvider.jsx'
import { PLATFORMS, addCustom, removeCustom } from '@/lib/practice/state.js'

const fieldClass =
  'rounded-lg border border-line bg-canvas px-3 py-2 text-sm text-ink placeholder:text-faint focus:border-accent focus:outline-none'

const newId = () => `c-${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}`

/** Lets the learner keep their own list of problems for a subject: a link, or a number on a known platform. */
export default function CustomProblems({ subject }) {
  const { state, update } = usePractice()
  const items = state.custom[subject.id] ?? []
  const [title, setTitle] = useState('')
  const [platform, setPlatform] = useState(PLATFORMS[0])
  const [link, setLink] = useState('')
  const [error, setError] = useState('')

  const submit = (event) => {
    event.preventDefault()
    const next = addCustom(state, subject.id, { title, platform, link }, newId())
    if (next === state) {
      setError(
        platform === 'Other'
          ? 'For "Other", paste the full link (it starts with https://).'
          : 'Paste a link, or type a problem number or name for this platform.',
      )
      return
    }
    update((s) => addCustom(s, subject.id, { title, platform, link }, newId()))
    setTitle('')
    setLink('')
    setError('')
  }

  return (
    <section className="mt-10" aria-labelledby="custom-heading">
      <h2 id="custom-heading" className="font-display text-lg font-semibold">
        Your own problems
      </h2>
      <p className="mt-1 text-sm text-muted">
        Found a good question on LeetCode, GeeksforGeeks or anywhere else? Add it here with its link or problem number
        and tick it off with the others.
      </p>

      {items.length > 0 && (
        <ul className="mt-4 space-y-2">
          {items.map((item) => (
            <li key={item.id} className="flex items-center gap-3 rounded-xl border border-line bg-panel px-4 py-3">
              <DoneToggle id={item.id} />
              <div className="min-w-0 flex-1">
                <p className="truncate font-medium">{item.title}</p>
                <p className="text-xs text-muted">{item.platform}</p>
              </div>
              <a
                href={item.url}
                target="_blank"
                rel="noreferrer noopener"
                className="inline-flex items-center gap-1.5 rounded-full border border-line-strong px-3 py-1.5 text-sm hover:border-accent"
              >
                Open <ExternalLink size={13} />
              </a>
              <button
                type="button"
                onClick={() => update((s) => removeCustom(s, subject.id, item.id))}
                aria-label={`Remove ${item.title}`}
                className="grid size-8 place-items-center rounded-full text-muted hover:bg-panel-2 hover:text-danger"
              >
                <Trash2 size={15} />
              </button>
            </li>
          ))}
        </ul>
      )}

      <form onSubmit={submit} className="mt-4 grid gap-2 sm:grid-cols-[1fr_9rem_1fr_auto]">
        <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Title (optional)" aria-label="Problem title" className={fieldClass} />
        <select value={platform} onChange={(e) => setPlatform(e.target.value)} aria-label="Platform" className={fieldClass}>
          {PLATFORMS.map((p) => (
            <option key={p}>{p}</option>
          ))}
        </select>
        <input value={link} onChange={(e) => setLink(e.target.value)} placeholder="Link, or problem number" aria-label="Link or problem number" className={fieldClass} />
        <button type="submit" className="inline-flex items-center justify-center gap-1.5 rounded-lg bg-linear-to-r from-accent to-accent-2 px-4 py-2 text-sm font-semibold text-white">
          <Plus size={15} /> Add
        </button>
      </form>
      {error && <p className="mt-2 text-xs text-warn" role="alert">{error}</p>}
    </section>
  )
}
