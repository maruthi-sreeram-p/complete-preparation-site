import { useMemo } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, BookOpenCheck, ListChecks, Play, Waypoints } from 'lucide-react'
import ProgressBar from '@/components/ui/ProgressBar.jsx'
import ProgressRing from '@/components/ui/ProgressRing.jsx'
import { listRoadmaps } from '@/lib/content/registry.js'
import { computeStats, pickContinueTarget, statusOfTopic } from '@/lib/progress/state.js'
import { STATUS } from '@/lib/progress/status.js'
import { useProgressStore } from '@/features/progress/ProgressProvider.jsx'
import { paths } from '@/lib/util.js'

const HOW_IT_WORKS = [
  {
    Icon: Waypoints,
    title: 'Follow the tree',
    text: 'Every step is numbered, so you always know what comes first and what comes next.',
  },
  {
    Icon: BookOpenCheck,
    title: 'Read chapter by chapter',
    text: 'Diagrams, code, tables and interview notes from your guides, on clean web pages.',
  },
  {
    Icon: ListChecks,
    title: 'Track and practise',
    text: 'Tick off chapters, answer the practice questions and pick up where you left off.',
  },
]

export default function HomePage() {
  const { state } = useProgressStore()
  const roadmaps = listRoadmaps()
  const roadmap = roadmaps.find((r) => r.id === state.activeRoadmapId) ?? roadmaps[0]

  if (!roadmap) {
    return (
      <div className="mx-auto max-w-lg px-4 py-24 text-center">
        <h1 className="text-xl font-semibold">No roadmap found</h1>
        <p className="mt-2 text-sm text-muted">
          Add <code className="rounded bg-panel-2 px-1.5 py-0.5 font-mono text-xs">content/roadmaps/&lt;id&gt;/roadmap.json</code>{' '}
          to get started. See <code className="rounded bg-panel-2 px-1.5 py-0.5 font-mono text-xs">content/README.md</code>.
        </p>
      </div>
    )
  }
  return <Home roadmap={roadmap} progress={state.roadmaps[roadmap.id]} />
}

function Home({ roadmap, progress }) {
  const stats = useMemo(() => computeStats(roadmap, progress), [roadmap, progress])
  const target = useMemo(() => pickContinueTarget(roadmap, progress), [roadmap, progress])
  const guides = useMemo(
    () => new Set(roadmap.topics.map((t) => t.source?.document).filter((d) => d?.endsWith('.pdf'))).size,
    [roadmap],
  )
  const started = stats.completed + stats.inProgress > 0 || target?.reason === 'resume'

  const facts = [
    [stats.byCategory.length, 'stages'],
    [stats.total, 'steps'],
    [stats.subtopics.total, 'chapters'],
    [guides, 'guides'],
  ]

  return (
    <div className="w-full space-y-10 px-4 py-8 lg:px-6 lg:py-12">
      <section className="grid items-center gap-8 lg:grid-cols-[minmax(0,1fr)_auto]">
        <div>
          <div className="text-sm font-medium text-accent">Your interview preparation</div>
          <h1 className="mt-3 text-4xl font-semibold tracking-tight sm:text-5xl">{roadmap.title}</h1>
          <p className="mt-4 max-w-3xl text-lg text-muted">
            All your guides turned into one clear path, from your first Java class to your final mock interview. Open a
            step, study it, and move on to the next.
          </p>
          <div className="mt-6 flex flex-wrap items-center gap-3">
            {target && (
              <Link
                to={paths.topic(roadmap.id, target.topic.id)}
                className="inline-flex items-center gap-2 rounded-lg bg-ink px-4 py-2.5 text-sm font-medium text-canvas"
              >
                <Play size={15} /> {started ? 'Continue learning' : 'Start learning'}
              </Link>
            )}
            <Link
              to={paths.roadmap(roadmap.id)}
              className="inline-flex items-center gap-2 rounded-lg border border-line-strong bg-panel px-4 py-2.5 text-sm font-medium transition-colors hover:border-accent/60"
            >
              <Waypoints size={15} /> View the roadmap
            </Link>
          </div>
          {target && (
            <p className="mt-3 text-sm text-faint">
              {started ? 'You are on' : 'First step'}: {target.topic.title}
            </p>
          )}
        </div>

        <div className="flex items-center gap-6 rounded-2xl border border-line bg-panel p-6">
          <ProgressRing value={stats.percent} />
          <dl className="grid grid-cols-2 gap-x-6 gap-y-3">
            {facts.map(([value, label]) => (
              <div key={label}>
                <dd className="text-xl font-semibold tabular-nums">{value}</dd>
                <dt className="text-xs text-faint">{label}</dt>
              </div>
            ))}
          </dl>
        </div>
      </section>

      <section>
        <h2 className="mb-4 text-lg font-semibold tracking-tight">The path, in order</h2>
        <ol className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4">
          {stats.byCategory.map(({ category, total, completed, percent }, i) => {
            const steps = roadmap.topics.filter((t) => t.categoryId === category.id)
            const next = steps.find((t) => statusOfTopic(progress, t.id) !== STATUS.COMPLETED) ?? steps[0]
            const chapters = steps.reduce((sum, t) => sum + t.subtopics.length, 0)
            return (
              <li key={category.id}>
                <Link
                  to={paths.topic(roadmap.id, next.id)}
                  className="group flex h-full flex-col rounded-xl border border-line bg-panel p-4 transition-colors hover:border-line-strong"
                >
                  <div className="flex items-start gap-3">
                    <span
                      className="grid size-7 shrink-0 place-items-center rounded-full text-xs font-semibold text-white"
                      style={{ background: category.color }}
                    >
                      {i + 1}
                    </span>
                    <div className="min-w-0 flex-1">
                      <div className="text-sm font-medium">{category.title}</div>
                      <p className="mt-1 text-xs text-muted">{category.description}</p>
                    </div>
                    <ArrowRight size={14} className="mt-0.5 shrink-0 text-faint transition-transform group-hover:translate-x-0.5" />
                  </div>
                  <div className="mt-auto pt-4">
                    <ProgressBar value={percent} color={category.color} />
                    <div className="mt-2 text-xs tabular-nums text-faint">
                      {completed}/{total} steps{chapters > 0 && ` · ${chapters} chapters`}
                    </div>
                  </div>
                </Link>
              </li>
            )
          })}
        </ol>
      </section>

      <section className="grid gap-3 md:grid-cols-3">
        {HOW_IT_WORKS.map(({ Icon, title, text }) => (
          <div key={title} className="rounded-xl border border-line bg-panel p-4">
            <Icon size={18} className="text-accent" />
            <div className="mt-2 text-sm font-medium">{title}</div>
            <p className="mt-1 text-sm text-muted">{text}</p>
          </div>
        ))}
      </section>
    </div>
  )
}
