import { useEffect, useRef, useState } from 'react'
import { Check, CheckCheck, ExternalLink, Eye, EyeOff, Lightbulb, Lock, Play } from 'lucide-react'
import Markdown from '@/features/content/blocks/Markdown.jsx'
import { usePractice } from './PracticeProvider.jsx'
import { isDone, setAnswer, setDone } from '@/lib/practice/state.js'
import { MAX_ROWS_SHOWN, checkAnswer, loadSqlEngine, runQuery } from '@/lib/practice/sql.js'
import { cn } from '@/lib/util.js'

export const LEVEL_STYLE = {
  Easy: 'border-ok/40 text-ok',
  Medium: 'border-warn/40 text-warn',
  Hard: 'border-danger/40 text-danger',
}

const textareaClass =
  'w-full resize-y rounded-lg border border-line bg-canvas p-3 text-sm leading-relaxed text-ink placeholder:text-faint focus:border-accent focus:outline-none'

/** A textarea value that is saved shortly after the learner stops typing, and once more when the card closes. */
function useSavedText(id) {
  const { state, update } = usePractice()
  const [text, setText] = useState(state.answers[id] ?? '')
  const latest = useRef(text)
  const timer = useRef(null)

  const change = (value) => {
    setText(value)
    latest.current = value
    clearTimeout(timer.current)
    timer.current = setTimeout(() => update((s) => setAnswer(s, id, latest.current)), 400)
  }
  useEffect(
    () => () => {
      clearTimeout(timer.current)
      update((s) => setAnswer(s, id, latest.current))
    },
    [id, update],
  )
  return [text, change]
}

export function DoneToggle({ id, label = 'Mark as done' }) {
  const { state, update } = usePractice()
  const done = isDone(state, id)
  return (
    <button
      type="button"
      onClick={() => update((s) => setDone(s, id, !done))}
      aria-pressed={done}
      aria-label={done ? 'Done. Click to undo.' : label}
      title={done ? 'Done. Click to undo.' : label}
      className={cn(
        'grid size-7 shrink-0 place-items-center rounded-full border transition-colors',
        done ? 'border-ok bg-ok text-canvas' : 'border-line-strong text-transparent hover:border-ok hover:text-ok',
      )}
    >
      <Check size={15} strokeWidth={3} />
    </button>
  )
}

export function LevelBadge({ level }) {
  if (!level) return null
  return <span className={cn('shrink-0 rounded-full border px-2 py-0.5 text-[11px] font-medium', LEVEL_STYLE[level] ?? 'border-line text-muted')}>{level}</span>
}

export function ResultTable({ columns, rows }) {
  const shown = rows.slice(0, MAX_ROWS_SHOWN)
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map((c, i) => (
              <th key={i}>{c}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {shown.map((row, i) => (
            <tr key={i}>
              {row.map((cell, j) => (
                <td key={j}>{cell === null ? <span className="text-faint italic">NULL</span> : String(cell)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {rows.length > shown.length && <p className="p-2 text-xs text-muted">Showing the first {shown.length} of {rows.length} rows.</p>}
      {rows.length === 0 && <p className="p-2 text-xs text-muted">No rows.</p>}
    </div>
  )
}

function Reveal({ label, hideLabel, children, icon: Icon = Eye }) {
  const [open, setOpen] = useState(false)
  return (
    <div>
      <button type="button" onClick={() => setOpen(!open)} className="inline-flex items-center gap-1.5 text-xs font-medium text-accent hover:text-ink">
        {open ? <EyeOff size={14} /> : <Icon size={14} />} {open ? hideLabel : label}
      </button>
      {open && <div className="mt-2 rounded-lg border border-line bg-panel-2 p-3">{children}</div>}
    </div>
  )
}

function SqlQuestion({ question, subject }) {
  const { update } = usePractice()
  const [query, setQuery] = useSavedText(question.id)
  const [busy, setBusy] = useState(false)
  const [outcome, setOutcome] = useState(null)

  const execute = async (mode) => {
    if (!query.trim() || busy) return
    setBusy(true)
    try {
      const SQL = await loadSqlEngine()
      const result =
        mode === 'check'
          ? checkAnswer(SQL, subject.dataset.sql, query, question.solution, { ordered: question.ordered })
          : runQuery(SQL, subject.dataset.sql, query)
      setOutcome({ mode, ...result })
      if (mode === 'check' && result.match) update((s) => setDone(s, question.id, true))
    } catch (error) {
      setOutcome({ mode, ok: false, error: `The SQL engine could not be loaded (${error.message}). Check your connection and try again.` })
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mt-3 space-y-3">
      <textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={(e) => {
          if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault()
            execute('run')
          }
        }}
        rows={5}
        spellCheck={false}
        aria-label="Your SQL query"
        placeholder="-- write your query here (Ctrl+Enter runs it)"
        className={cn(textareaClass, 'font-mono')}
      />
      <div className="flex flex-wrap items-center gap-2">
        <button type="button" onClick={() => execute('run')} disabled={busy || !query.trim()} className="inline-flex items-center gap-1.5 rounded-full border border-line-strong bg-panel-2 px-4 py-1.5 text-sm font-medium transition-colors hover:border-accent disabled:opacity-50">
          <Play size={14} /> Run
        </button>
        <button type="button" onClick={() => execute('check')} disabled={busy || !query.trim()} className="inline-flex items-center gap-1.5 rounded-full bg-linear-to-r from-accent to-accent-2 px-4 py-1.5 text-sm font-semibold text-white disabled:opacity-50">
          <CheckCheck size={14} /> Check answer
        </button>
        {busy && <span className="text-xs text-muted">Running…</span>}
        {question.ordered && <span className="text-xs text-faint">Row order counts in this question.</span>}
      </div>

      {outcome && (
        <div className="space-y-2" aria-live="polite">
          {!outcome.ok && <p className="rounded-lg border border-danger/40 bg-danger/5 p-3 font-mono text-xs text-danger">{outcome.error}</p>}
          {outcome.ok && outcome.mode === 'check' && (
            <p className={cn('rounded-lg border p-3 text-sm', outcome.match ? 'border-ok/40 bg-ok/5 text-ok' : 'border-warn/40 bg-warn/5 text-warn')}>
              {outcome.match ? 'Correct. Your result matches the expected one.' : `Not quite. ${outcome.reason}`}
            </p>
          )}
          {outcome.ok && outcome.message && <p className="text-xs text-muted">{outcome.message}</p>}
          {outcome.ok && outcome.columns.length > 0 && <ResultTable columns={outcome.columns} rows={outcome.rows} />}
        </div>
      )}

      {question.hint && (
        <Reveal label="Show hint" hideLabel="Hide hint" icon={Lightbulb}>
          <Markdown>{question.hint}</Markdown>
        </Reveal>
      )}
      <Reveal label="Show a solution" hideLabel="Hide solution">
        <Markdown>{`\`\`\`sql\n${question.solution}\n\`\`\`${question.explanation ? `\n\n${question.explanation}` : ''}`}</Markdown>
      </Reveal>
    </div>
  )
}

function WrittenQuestion({ question }) {
  const [text, setText] = useSavedText(question.id)
  return (
    <div className="mt-3 space-y-3">
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={5}
        aria-label="Your answer"
        placeholder="Write your answer here. It is saved in this browser."
        className={textareaClass}
      />
      {question.hint && (
        <Reveal label="Show hint" hideLabel="Hide hint" icon={Lightbulb}>
          <Markdown>{question.hint}</Markdown>
        </Reveal>
      )}
      {question.answer && (
        <Reveal label="Compare with the model answer" hideLabel="Hide model answer">
          <Markdown>{question.answer}</Markdown>
        </Reveal>
      )}
    </div>
  )
}

function CodingQuestion({ question }) {
  const [notes, setNotes] = useSavedText(question.id)
  const links = question.links ?? []
  return (
    <div className="mt-3 space-y-3">
      {links.length > 0 && (
        <ul className="flex flex-wrap gap-2">
          {links.map((link) => (
            <li key={link.url}>
              <a
                href={link.url}
                target="_blank"
                rel="noreferrer noopener"
                className="inline-flex items-center gap-1.5 rounded-full border border-line-strong bg-panel-2 px-3 py-1.5 text-sm transition-colors hover:border-accent"
              >
                <span className="text-xs font-semibold text-accent">{link.platform}</span>
                {link.number != null && <span className="tabular-nums text-muted">#{link.number}</span>}
                {link.label && link.label !== question.title && <span>{link.label}</span>}
                {link.premium && <Lock size={12} className="text-warn" aria-label="Needs a premium account" />}
                <ExternalLink size={13} className="text-faint" />
              </a>
            </li>
          ))}
        </ul>
      )}
      <textarea
        value={notes}
        onChange={(e) => setNotes(e.target.value)}
        rows={3}
        aria-label="Your notes"
        placeholder="Notes: the idea, the complexity, what tripped you up. Saved in this browser."
        className={textareaClass}
      />
      {question.hint && (
        <Reveal label="Show hint" hideLabel="Hide hint" icon={Lightbulb}>
          <Markdown>{question.hint}</Markdown>
        </Reveal>
      )}
    </div>
  )
}

export default function QuestionCard({ question, index, subject }) {
  const type = question.type ?? 'written'
  return (
    <li id={`q-${question.id}`} className="rounded-xl border border-line bg-panel p-4 sm:p-5">
      <div className="flex items-start gap-3">
        <DoneToggle id={question.id} />
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
            <span className="text-sm font-semibold tabular-nums text-accent">{index}</span>
            <h3 className="min-w-0 flex-1 font-medium">{question.title}</h3>
            {type === 'sql' && <span className="rounded-full border border-line px-2 py-0.5 text-[11px] text-muted">SQL</span>}
            <LevelBadge level={question.level} />
          </div>
          {question.prompt && (
            <div className="mt-2 text-sm">
              <Markdown>{question.prompt}</Markdown>
            </div>
          )}
          {type === 'sql' && subject.dataset && question.solution ? (
            <SqlQuestion question={question} subject={subject} />
          ) : type === 'coding' ? (
            <CodingQuestion question={question} />
          ) : (
            <WrittenQuestion question={question} />
          )}
        </div>
      </div>
    </li>
  )
}
