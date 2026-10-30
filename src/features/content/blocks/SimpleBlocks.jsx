import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowUpRight, Globe, Info, Lightbulb, ListChecks, MessageSquareQuote, Star, TriangleAlert } from 'lucide-react'
import { useRoadmapScope } from '@/features/roadmap/RoadmapScope.jsx'
import StatusIcon from '@/components/ui/StatusIcon.jsx'
import { cn, paths } from '@/lib/util.js'
import Markdown from './Markdown.jsx'

export function TableBlock({ caption, headers = [], rows = [] }) {
  return (
    <div className="doc">
      <div className="table-wrap">
        <table>
          {headers.length > 0 && (
            <thead>
              <tr>
                {headers.map((h, i) => (
                  <th key={i}>
                    <Markdown inline>{String(h)}</Markdown>
                  </th>
                ))}
              </tr>
            </thead>
          )}
          <tbody>
            {rows.map((row, r) => (
              <tr key={r}>
                {row.map((cell, c) => (
                  <td key={c}>
                    <Markdown inline>{String(cell ?? '')}</Markdown>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {caption && <p className="mt-2 text-xs text-faint">{caption}</p>}
    </div>
  )
}

const CALLOUTS = {
  note: { Icon: Info, box: 'border-accent-2/30 bg-accent-2/5', icon: 'text-accent-2' },
  tip: { Icon: Lightbulb, box: 'border-ok/30 bg-ok/5', icon: 'text-ok' },
  warning: { Icon: TriangleAlert, box: 'border-warn/30 bg-warn/5', icon: 'text-warn' },
  important: { Icon: Star, box: 'border-accent/35 bg-accent/5', icon: 'text-accent' },
  interview: { Icon: MessageSquareQuote, box: 'border-accent/35 bg-accent/5', icon: 'text-accent' },
  realworld: { Icon: Globe, box: 'border-accent-2/30 bg-accent-2/5', icon: 'text-accent-2' },
  keypoints: { Icon: ListChecks, box: 'border-line-strong bg-panel-2/60', icon: 'text-muted' },
}

export function CalloutBlock({ variant = 'note', title, text }) {
  const { Icon, box, icon } = CALLOUTS[variant] ?? CALLOUTS.note
  return (
    <div className={cn('flex gap-3 rounded-xl border p-4', box)}>
      <Icon size={17} className={cn('mt-0.5 shrink-0', icon)} />
      <div className="min-w-0">
        {title && <div className="mb-0.5 text-sm font-medium">{title}</div>}
        <Markdown>{text}</Markdown>
      </div>
    </div>
  )
}

/**
 * A figure from the source document that has not been turned into a diagram yet.
 * Shows the caption and the labels found in the original so nothing is lost.
 */
export function FigureBlock({ caption, labels = [] }) {
  return (
    <figure className="rounded-xl border border-dashed border-line-strong bg-panel p-4">
      <figcaption className="text-sm">{caption}</figcaption>
      {labels.length > 0 && (
        <ul className="mt-2 flex flex-wrap gap-1.5">
          {labels.map((label, i) => (
            <li key={i} className="rounded-md border border-line px-2 py-0.5 text-xs text-muted">
              {label}
            </li>
          ))}
        </ul>
      )}
      <p className="mt-2 text-xs text-faint">Diagram not generated yet.</p>
    </figure>
  )
}

export function StepsBlock({ title, steps = [] }) {
  return (
    <div>
      {title && <h4 className="mb-3 text-sm font-medium text-muted">{title}</h4>}
      <ol className="relative space-y-5 border-l border-line pl-7">
        {steps.map((step, i) => (
          <li key={i} className="relative">
            <span className="absolute -left-[2.35rem] grid size-7 place-items-center rounded-full border border-accent/40 bg-canvas text-xs font-semibold text-accent">
              {i + 1}
            </span>
            {step.title && <div className="text-sm font-medium">{step.title}</div>}
            <Markdown>{step.text}</Markdown>
          </li>
        ))}
      </ol>
    </div>
  )
}

export function QuestionsBlock({ items = [] }) {
  return (
    <ol className="space-y-3">
      {items.map((item, i) => (
        <Question key={i} index={i + 1} {...item} />
      ))}
    </ol>
  )
}

function Question({ index, question, hint, answer, difficulty }) {
  const [showHint, setShowHint] = useState(false)
  const [showAnswer, setShowAnswer] = useState(false)
  return (
    <li className="rounded-xl border border-line bg-panel p-4">
      <div className="flex gap-3">
        <span className="text-sm font-semibold tabular-nums text-accent">Q{index}</span>
        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-3">
            <div className="text-sm font-medium">
              <Markdown inline>{question}</Markdown>
            </div>
            {difficulty && <span className="shrink-0 rounded-full border border-line px-2 py-0.5 text-[11px] text-muted">{difficulty}</span>}
          </div>
          <div className="mt-3 flex gap-2">
            {hint && (
              <button type="button" onClick={() => setShowHint(!showHint)} className="text-xs text-muted hover:text-ink">
                {showHint ? 'Hide hint' : 'Show hint'}
              </button>
            )}
            {answer && (
              <button type="button" onClick={() => setShowAnswer(!showAnswer)} className="text-xs text-accent hover:text-ink">
                {showAnswer ? 'Hide answer' : 'Show answer'}
              </button>
            )}
          </div>
          {showHint && hint && (
            <div className="mt-2 rounded-lg bg-panel-2 p-3">
              <Markdown>{hint}</Markdown>
            </div>
          )}
          {showAnswer && answer && (
            <div className="mt-2 rounded-lg border border-line bg-panel-2 p-3">
              <Markdown>{answer}</Markdown>
            </div>
          )}
        </div>
      </div>
    </li>
  )
}

/** Links to other topics of the same roadmap, by id. Unknown ids are skipped. */
export function RelatedBlock({ topics = [] }) {
  const { roadmap, statusOf } = useRoadmapScope()
  const related = topics.map((id) => roadmap.topicsById[id]).filter(Boolean)
  if (related.length === 0) return null
  return <TopicChips topics={related} roadmapId={roadmap.id} statusOf={statusOf} />
}

export function TopicChips({ topics, roadmapId, statusOf }) {
  return (
    <ul className="flex flex-wrap gap-2">
      {topics.map((topic) => (
        <li key={topic.id}>
          <Link
            to={paths.topic(roadmapId, topic.id)}
            className="inline-flex items-center gap-2 rounded-lg border border-line bg-panel px-3 py-1.5 text-sm text-muted transition-colors hover:border-line-strong hover:text-ink"
          >
            <StatusIcon status={statusOf(topic.id)} size={14} />
            {topic.title}
            <ArrowUpRight size={13} className="text-faint" />
          </Link>
        </li>
      ))}
    </ul>
  )
}
