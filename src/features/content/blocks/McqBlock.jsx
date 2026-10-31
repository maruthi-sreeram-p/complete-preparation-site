import { useMemo, useState } from 'react'
import { Check, ChevronLeft, ChevronRight, RotateCcw, X } from 'lucide-react'
import { cn } from '@/lib/util.js'
import Markdown from './Markdown.jsx'

const PAGE_SIZE = 20
const LETTERS = 'ABCD'

const svgSrc = (svg) => `data:image/svg+xml,${encodeURIComponent(svg)}`

function readAnswers(key) {
  try {
    return JSON.parse(localStorage.getItem(key)) ?? {}
  } catch {
    return {}
  }
}

function writeAnswers(key, answers) {
  try {
    localStorage.setItem(key, JSON.stringify(answers))
  } catch {
    // answers then last only for this visit
  }
}

/**
 * Multiple-choice practice: pick an answer to see whether it is right and why.
 * block: { id, items: [{ t: type, q: markdown, o: options, a: answer index, w: why, svg?, os?: option svgs }] }
 * Only one page of questions is on screen at a time, so a chapter with a thousand stays fast.
 */
export default function McqBlock({ id, items = [] }) {
  const storageKey = `prep-site:mcq:${id}`
  const [answers, setAnswers] = useState(() => readAnswers(storageKey))
  const [type, setType] = useState(null)
  const [page, setPage] = useState(0)

  const numbered = useMemo(() => items.map((item, index) => ({ ...item, index })), [items])
  const types = useMemo(() => {
    const counts = new Map()
    for (const item of items) counts.set(item.t, (counts.get(item.t) ?? 0) + 1)
    return [...counts]
  }, [items])
  const shown = useMemo(() => (type ? numbered.filter((item) => item.t === type) : numbered), [numbered, type])

  const pages = Math.max(1, Math.ceil(shown.length / PAGE_SIZE))
  const current = Math.min(page, pages - 1)
  const visible = shown.slice(current * PAGE_SIZE, (current + 1) * PAGE_SIZE)

  const attempted = shown.filter((item) => answers[item.index] !== undefined)
  const correct = attempted.filter((item) => answers[item.index] === item.a).length

  const answer = (index, choice) => {
    const next = { ...answers, [index]: choice }
    setAnswers(next)
    writeAnswers(storageKey, next)
  }
  const reset = () => {
    setAnswers({})
    writeAnswers(storageKey, {})
    setPage(0)
  }

  const pager = (
    <div className="flex items-center justify-between gap-3 text-sm text-muted">
      <button
        type="button"
        disabled={current === 0}
        onClick={() => setPage(current - 1)}
        className="inline-flex items-center gap-1 rounded-lg border border-line bg-panel px-3 py-1.5 hover:border-accent disabled:opacity-40"
      >
        <ChevronLeft size={15} /> Previous
      </button>
      <span className="tabular-nums">
        Page {current + 1} of {pages}
      </span>
      <button
        type="button"
        disabled={current >= pages - 1}
        onClick={() => setPage(current + 1)}
        className="inline-flex items-center gap-1 rounded-lg border border-line bg-panel px-3 py-1.5 hover:border-accent disabled:opacity-40"
      >
        Next <ChevronRight size={15} />
      </button>
    </div>
  )

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="text-sm text-muted tabular-nums">
          <span className="font-semibold text-ink">{shown.length}</span> questions · {attempted.length} answered ·{' '}
          <span className="text-ok">{correct} correct</span>
          {attempted.length > 0 && ` (${Math.round((correct / attempted.length) * 100)}%)`}
        </div>
        <button
          type="button"
          onClick={reset}
          className="inline-flex items-center gap-1.5 text-sm text-muted hover:text-ink"
        >
          <RotateCcw size={14} /> Start again
        </button>
      </div>

      {types.length > 1 && (
        <div className="flex flex-wrap gap-1.5">
          <TypeChip active={type === null} onClick={() => (setType(null), setPage(0))}>
            All types ({items.length})
          </TypeChip>
          {types.map(([name, count]) => (
            <TypeChip key={name} active={type === name} onClick={() => (setType(name), setPage(0))}>
              {name} ({count})
            </TypeChip>
          ))}
        </div>
      )}

      {pages > 1 && pager}
      <ol className="space-y-4">
        {visible.map((item) => (
          <Question
            key={item.index}
            item={item}
            number={numbered.indexOf(item) + 1}
            chosen={answers[item.index]}
            onChoose={(choice) => answer(item.index, choice)}
          />
        ))}
      </ol>
      {pages > 1 && pager}
    </div>
  )
}

function TypeChip({ active, onClick, children }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'rounded-full border px-2.5 py-1 text-xs transition-colors',
        active ? 'border-accent bg-accent/15 text-ink' : 'border-line bg-panel text-muted hover:border-line-strong',
      )}
    >
      {children}
    </button>
  )
}

function Question({ item, number, chosen, onChoose }) {
  const done = chosen !== undefined
  return (
    <li className="rounded-xl border border-line bg-panel p-4">
      <div className="mb-1 text-xs text-faint">
        Q{number} · {item.t}
      </div>
      <Markdown>{item.q}</Markdown>
      {item.svg && <img src={svgSrc(item.svg)} alt="Figure for this question" className="mt-3 rounded-lg bg-white p-2" />}
      <div className="mt-3 grid gap-2 sm:grid-cols-2">
        {item.o.map((option, i) => {
          const isAnswer = i === item.a
          return (
            <button
              key={i}
              type="button"
              disabled={done}
              onClick={() => onChoose(i)}
              className={cn(
                'flex items-center gap-2.5 rounded-lg border px-3 py-2 text-left text-sm transition-colors',
                !done && 'border-line hover:border-accent',
                done && isAnswer && 'border-ok bg-ok/10',
                done && !isAnswer && chosen === i && 'border-danger bg-danger/10',
                done && !isAnswer && chosen !== i && 'border-line opacity-60',
              )}
            >
              <span className="shrink-0 font-mono text-xs text-faint">{LETTERS[i]}</span>
              {item.os ? (
                <img src={svgSrc(item.os[i])} alt={`Option ${LETTERS[i]}`} className="rounded bg-white p-1" />
              ) : (
                <span className="min-w-0">{option}</span>
              )}
              {done && isAnswer && <Check size={15} className="ml-auto shrink-0 text-ok" />}
              {done && !isAnswer && chosen === i && <X size={15} className="ml-auto shrink-0 text-danger" />}
            </button>
          )
        })}
      </div>
      {done && (
        <div className="mt-3 rounded-lg bg-panel-2/60 p-3 text-sm">
          <span className="font-medium">{chosen === item.a ? 'Correct. ' : `Answer: ${LETTERS[item.a]}. `}</span>
          <Markdown inline>{item.w}</Markdown>
        </div>
      )}
    </li>
  )
}
