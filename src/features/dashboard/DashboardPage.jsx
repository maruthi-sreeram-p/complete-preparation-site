import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, Info, Play, RotateCcw, Trophy } from 'lucide-react'
import { useRoadmapScope } from '@/features/roadmap/RoadmapScope.jsx'
import ProgressRing from '@/components/ui/ProgressRing.jsx'
import ProgressBar from '@/components/ui/ProgressBar.jsx'
import StatusIcon from '@/components/ui/StatusIcon.jsx'
import CategoryBadge from '@/components/ui/CategoryBadge.jsx'
import DataIssues from '@/components/ui/DataIssues.jsx'
import { STATUS } from '@/lib/progress/status.js'
import { cn, formatRelative, paths } from '@/lib/util.js'

export default function DashboardPage() {
  const { roadmap, stats, continueTarget } = useRoadmapScope()

  return (
    <div className="w-full space-y-6 px-4 py-8 lg:px-6">
      {roadmap.placeholder && (
        <div className="flex items-start gap-3 rounded-xl border border-accent/25 bg-accent/5 p-4 text-sm text-muted">
          <Info size={16} className="mt-0.5 shrink-0 text-accent" />
          <p>
            You are looking at <strong className="text-ink">placeholder data</strong>. Replace{' '}
            <code className="font-mono text-xs text-ink">content/roadmaps/{roadmap.id}/</code> with your own roadmap and
            topic content; see <code className="font-mono text-xs text-ink">content/README.md</code>.
          </p>
        </div>
      )}
      <DataIssues issues={roadmap.issues} />

      <div>
        <h1 className="text-2xl font-semibold tracking-tight">{roadmap.title}</h1>
        {roadmap.description && <p className="mt-1 max-w-2xl text-sm text-muted">{roadmap.description}</p>}
      </div>

      <div className="grid gap-4 lg:grid-cols-[1fr_auto]">
        <ContinueCard target={continueTarget} total={stats.total} />
        <OverallCard stats={stats} />
      </div>

      <section>
        <h2 className="mb-3 text-sm font-medium text-muted">Progress by category</h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4">
          {stats.byCategory.map(({ category, total, completed, inProgress, percent }) => (
            <div key={category.id} className="rounded-xl border border-line bg-panel p-4">
              <div className="flex items-center justify-between">
                <CategoryBadge category={category} className="text-sm text-ink" />
                <span className="text-xs tabular-nums text-muted">{percent}%</span>
              </div>
              <ProgressBar value={percent} color={category.color} className="mt-3" />
              <div className="mt-2 text-xs text-faint">
                {completed} of {total} completed{inProgress > 0 && ` · ${inProgress} in progress`}
              </div>
            </div>
          ))}
        </div>
      </section>

      <TopicLists />
    </div>
  )
}

function ContinueCard({ target, total }) {
  const { roadmap, lastStudiedAt, statusOf } = useRoadmapScope()

  if (total === 0) {
    return <div className="rounded-2xl border border-line bg-panel p-6 text-sm text-muted">No topics yet.</div>
  }
  if (!target) {
    return (
      <div className="flex items-center gap-4 rounded-2xl border border-ok/25 bg-ok/5 p-6">
        <Trophy size={28} className="text-ok" />
        <div>
          <div className="font-medium">Everything is completed</div>
          <div className="text-sm text-muted">Every topic in this roadmap is marked complete.</div>
        </div>
      </div>
    )
  }

  const { topic, reason } = target
  const studied = lastStudiedAt(topic.id)
  const category = roadmap.categoryById[topic.categoryId]
  return (
    <Link
      to={paths.topic(roadmap.id, topic.id)}
      className="group relative flex flex-col justify-between overflow-hidden rounded-2xl border border-line-strong bg-linear-to-br from-accent/15 via-panel to-accent-2/10 p-6 transition-colors hover:border-accent/50"
    >
      <div>
        <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wider text-accent">
          <Play size={12} /> {reason === 'resume' ? 'Continue learning' : 'Up next'}
        </div>
        <div className="mt-3 text-xl font-semibold tracking-tight">{topic.title}</div>
        {topic.summary && <p className="mt-1 line-clamp-2 max-w-xl text-sm text-muted">{topic.summary}</p>}
      </div>
      <div className="mt-6 flex items-center justify-between gap-4">
        <div className="flex min-w-0 items-center gap-3 text-xs text-muted">
          <StatusIcon status={statusOf(topic.id)} size={14} />
          <CategoryBadge category={category} />
          {studied && <span className="hidden text-faint sm:inline">studied {formatRelative(studied)}</span>}
        </div>
        <span className="inline-flex items-center gap-1.5 rounded-lg bg-ink px-3 py-1.5 text-sm font-medium text-canvas transition-transform group-hover:translate-x-0.5">
          Open <ArrowRight size={14} />
        </span>
      </div>
    </Link>
  )
}

function OverallCard({ stats }) {
  const { resetProgress } = useRoadmapScope()
  const [confirming, setConfirming] = useState(false)
  return (
    <div className="flex items-center gap-6 rounded-2xl border border-line bg-panel p-6">
      <ProgressRing value={stats.percent} />
      <dl className="space-y-1.5 text-sm">
        <Stat label="Completed" value={stats.completed} dot="bg-ok" />
        <Stat label="In progress" value={stats.inProgress} dot="bg-accent-2" />
        <Stat label="Not started" value={stats.notStarted} dot="bg-faint" />
        {stats.subtopics.total > 0 && (
          <div className="pt-1 text-xs text-faint">
            {stats.subtopics.done}/{stats.subtopics.total} subtopics done
          </div>
        )}
        <button
          type="button"
          onClick={() => {
            if (confirming) {
              resetProgress()
              setConfirming(false)
            } else {
              setConfirming(true)
            }
          }}
          onBlur={() => setConfirming(false)}
          className={cn(
            'mt-1 inline-flex items-center gap-1 text-xs transition-colors',
            confirming ? 'text-danger' : 'text-faint hover:text-muted',
          )}
        >
          <RotateCcw size={11} /> {confirming ? 'Click again to reset all progress' : 'Reset progress'}
        </button>
      </dl>
    </div>
  )
}

function Stat({ label, value, dot }) {
  return (
    <div className="flex items-center gap-2">
      <span className={cn('size-2 rounded-full', dot)} />
      <dt className="w-24 text-muted">{label}</dt>
      <dd className="font-medium tabular-nums">{value}</dd>
    </div>
  )
}

const TABS = [
  { id: 'recent', label: 'Recently studied' },
  { id: 'pending', label: 'Pending' },
  { id: 'completed', label: 'Completed' },
]

function TopicLists() {
  const { roadmap, recent, statusOf, lastStudiedAt } = useRoadmapScope()
  const [tab, setTab] = useState('recent')

  const inSequence = roadmap.sequence.map((id) => roadmap.topicsById[id])
  const lists = {
    recent,
    pending: inSequence.filter((t) => statusOf(t.id) !== STATUS.COMPLETED),
    completed: inSequence.filter((t) => statusOf(t.id) === STATUS.COMPLETED),
  }
  const items = lists[tab]
  const empty = {
    recent: 'Topics you open will show up here.',
    pending: 'Nothing pending.',
    completed: 'No completed topics yet.',
  }

  return (
    <section>
      <div role="tablist" className="mb-3 flex gap-1 border-b border-line">
        {TABS.map(({ id, label }) => (
          <button
            key={id}
            role="tab"
            aria-selected={tab === id}
            onClick={() => setTab(id)}
            className={cn(
              '-mb-px border-b-2 px-3 py-2 text-sm transition-colors',
              tab === id ? 'border-accent text-ink' : 'border-transparent text-muted hover:text-ink',
            )}
          >
            {label} <span className="ml-1 text-xs tabular-nums text-faint">{lists[id].length}</span>
          </button>
        ))}
      </div>
      {items.length === 0 ? (
        <p className="py-6 text-sm text-faint">{empty[tab]}</p>
      ) : (
        <ul className="divide-y divide-line overflow-hidden rounded-xl border border-line bg-panel">
          {items.map((topic) => (
            <li key={topic.id}>
              <Link
                to={paths.topic(roadmap.id, topic.id)}
                className="flex items-center gap-3 px-4 py-3 transition-colors hover:bg-panel-2"
              >
                <StatusIcon status={statusOf(topic.id)} size={16} />
                <span className="min-w-0 flex-1 truncate text-sm">{topic.title}</span>
                <CategoryBadge category={roadmap.categoryById[topic.categoryId]} className="hidden sm:inline-flex" />
                {tab === 'recent' && (
                  <span className="w-20 text-right text-xs text-faint">{formatRelative(lastStudiedAt(topic.id))}</span>
                )}
              </Link>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
