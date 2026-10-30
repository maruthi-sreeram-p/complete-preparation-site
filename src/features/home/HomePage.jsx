import { useMemo } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, Play, Waypoints } from 'lucide-react'
import Wordmark from '@/components/ui/Wordmark.jsx'
import { listRoadmaps } from '@/lib/content/registry.js'
import { computeStats, pickContinueTarget, statusOfTopic } from '@/lib/progress/state.js'
import { STATUS } from '@/lib/progress/status.js'
import { useProgressStore } from '@/features/progress/ProgressProvider.jsx'
import { cn, paths } from '@/lib/util.js'

const WAYS = [
  ['01', 'Follow the trail', 'Every step is numbered, so you always know what comes first and what comes next.'],
  ['02', 'Learn it visually', 'Diagrams, code walkthroughs, tables and interview notes from your guides, chapter by chapter.'],
  ['03', 'Prove you know it', 'Answer the practice questions, tick off each chapter and pick up exactly where you left off.'],
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
  const stepNumber = target ? roadmap.sequence.indexOf(target.topic.id) + 1 : roadmap.sequence.length

  const stops = useMemo(
    () =>
      stats.byCategory.map(({ category, total, completed }) => {
        const steps = roadmap.topics.filter((t) => t.categoryId === category.id)
        const next = steps.find((t) => statusOfTopic(progress, t.id) !== STATUS.COMPLETED) ?? steps[0]
        return { category, total, completed, next }
      }),
    [stats, roadmap, progress],
  )
  const currentStop = target ? stops.findIndex((s) => s.category.id === target.topic.categoryId) : stops.length

  const facts = [
    [stats.total, 'steps'],
    [stats.subtopics.total, 'chapters'],
    [guides, 'guides'],
    [stops.length, 'stages'],
  ]

  return (
    <div className="overflow-x-clip">
      {/* ---- hero ---- */}
      <section className="relative isolate flex min-h-[calc(100dvh-3.5rem)] flex-col items-center justify-center px-4 py-16 text-center">
        <div
          aria-hidden="true"
          className="absolute top-1/2 left-1/2 -z-10 h-[60vh] w-[80vw] -translate-x-1/2 -translate-y-1/2 rounded-full"
          style={{
            background:
              'radial-gradient(closest-side, color-mix(in srgb, var(--color-accent) 22%, transparent), transparent)',
          }}
        />
        <span className="logo-mark size-16 sm:size-20" aria-hidden="true" />
        <h1 className="mt-4 text-[clamp(3.75rem,13vw,11rem)] leading-[0.95]">
          <Wordmark />
        </h1>
        <TrailFlourish />
        <p className="mt-6 font-display text-[clamp(1.25rem,2.6vw,2.25rem)] font-medium tracking-tight">
          From your first Java class to your final mock interview.
        </p>
        <p className="mt-3 max-w-2xl text-muted">
          One path through everything a Java full stack developer needs: the language, Spring, databases, system design,
          React and deployment.
        </p>

        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          {target && (
            <Link
              to={paths.topic(roadmap.id, target.topic.id)}
              className="inline-flex items-center gap-2 rounded-full bg-linear-to-r from-accent to-accent-2 px-6 py-3 font-semibold text-white shadow-lg"
            >
              <Play size={17} /> {started ? 'Continue the trail' : 'Start the trail'}
            </Link>
          )}
          <Link
            to={paths.roadmap(roadmap.id)}
            className="inline-flex items-center gap-2 rounded-full border border-line-strong bg-panel px-6 py-3 font-semibold transition-colors hover:border-accent"
          >
            <Waypoints size={17} /> See the full map
          </Link>
        </div>
        {started && target && (
          <p className="mt-4 text-sm text-muted">
            You are on step {stepNumber} of {stats.total}: {target.topic.title}
          </p>
        )}

        <dl className="mt-12 flex flex-wrap justify-center gap-x-12 gap-y-4">
          {facts.map(([value, label]) => (
            <div key={label}>
              <dd className="font-display text-4xl font-bold sm:text-5xl">{value}</dd>
              <dt className="mt-1 text-sm text-muted">{label}</dt>
            </div>
          ))}
        </dl>
      </section>

      {/* ---- the trail ---- */}
      <section className="px-4 py-16 lg:px-6">
        <div className="text-center">
          <h2 className="font-display text-4xl font-bold tracking-tight sm:text-5xl">The trail</h2>
          <p className="mt-3 text-muted">Eleven stages, in order. Click any stop to jump in.</p>
        </div>
        <WindingTrail roadmapId={roadmap.id} stops={stops} current={currentStop} />
        <VerticalTrail roadmapId={roadmap.id} stops={stops} current={currentStop} />
      </section>

      {/* ---- how ---- */}
      <section className="grid gap-10 px-4 py-16 md:grid-cols-3 lg:px-6">
        {WAYS.map(([number, title, text]) => (
          <div key={number}>
            <div className="bg-linear-to-r from-accent to-accent-2 bg-clip-text font-display text-7xl font-bold text-transparent">
              {number}
            </div>
            <h3 className="mt-3 font-display text-2xl font-bold tracking-tight">{title}</h3>
            <p className="mt-2 text-muted">{text}</p>
          </div>
        ))}
      </section>
    </div>
  )
}

/** A dashed path ending in a dot, drawn under the name: the brand's trail. */
function TrailFlourish() {
  return (
    <svg viewBox="0 0 400 40" aria-hidden="true" className="mt-3 w-[min(70vw,34rem)]">
      <path
        d="M4 28 C 70 4, 120 4, 190 22 S 320 36, 384 12"
        fill="none"
        stroke="var(--color-accent)"
        strokeWidth="3"
        strokeLinecap="round"
        strokeDasharray="1 10"
      />
      <circle cx="388" cy="10" r="6" fill="var(--color-accent-2)" />
    </svg>
  )
}

/** Stops along a winding line, for wide screens. */
function WindingTrail({ roadmapId, stops, current }) {
  const points = stops.map((_, i) => ({ x: ((i + 0.5) / stops.length) * 100, y: i % 2 === 0 ? 34 : 66 }))
  const segment = (a, b) => {
    const mid = (a.x + b.x) / 2
    return `C ${mid} ${a.y}, ${mid} ${b.y}, ${b.x} ${b.y}`
  }
  const pathTo = (end) =>
    points.slice(0, end + 1).reduce((d, p, i) => (i === 0 ? `M ${p.x} ${p.y}` : `${d} ${segment(points[i - 1], p)}`), '')

  return (
    <div className="relative mx-16 mt-6 hidden h-[26rem] lg:block">
      <svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true" className="absolute inset-0 size-full">
        <path
          d={pathTo(points.length - 1)}
          fill="none"
          stroke="var(--color-faint)"
          strokeWidth="3"
          strokeLinecap="round"
          strokeDasharray="1 9"
          vectorEffect="non-scaling-stroke"
        />
        {current > 0 && (
          <path
            d={pathTo(Math.min(current, points.length - 1))}
            fill="none"
            stroke="var(--color-accent)"
            strokeWidth="4"
            strokeLinecap="round"
            vectorEffect="non-scaling-stroke"
          />
        )}
      </svg>
      <ol>
        {stops.map((stop, i) => {
          const above = i % 2 === 0
          const here = i === current
          return (
            <li
              key={stop.category.id}
              className="absolute -translate-x-1/2 -translate-y-1/2"
              style={{ left: `${points[i].x}%`, top: `${points[i].y}%` }}
            >
              <Link to={paths.topic(roadmapId, stop.next.id)} className="group block">
                <StopBadge index={i} stop={stop} here={here} className="size-12 text-lg" />
                <div
                  className={cn(
                    'absolute left-1/2 -translate-x-1/2 text-center',
                    above ? 'bottom-full mb-3' : 'top-full mt-3',
                  )}
                  style={{ width: `min(${(2 / stops.length) * 92}vw, 15rem)` }}
                >
                  {here && <div className="mb-0.5 text-xs font-semibold text-accent">You are here</div>}
                  <div className="font-display text-sm leading-snug font-bold group-hover:text-accent xl:text-base">
                    {stop.category.title}
                  </div>
                  <div className="mt-0.5 text-xs text-faint tabular-nums">
                    {stop.completed}/{stop.total} steps
                  </div>
                </div>
              </Link>
            </li>
          )
        })}
      </ol>
    </div>
  )
}

/** The same stops as a vertical line, for narrow screens. */
function VerticalTrail({ roadmapId, stops, current }) {
  return (
    <ol className="mt-10 ml-5 space-y-6 border-l-2 border-dashed border-line-strong pl-8 lg:hidden">
      {stops.map((stop, i) => (
        <li key={stop.category.id} className="relative">
          <Link to={paths.topic(roadmapId, stop.next.id)} className="group flex items-center gap-1">
            <StopBadge index={i} stop={stop} here={i === current} className="absolute top-0 -left-[3.2rem] size-9 text-sm" />
            <div className="min-w-0">
              {i === current && <div className="text-xs font-semibold text-accent">You are here</div>}
              <div className="font-display font-bold group-hover:text-accent">{stop.category.title}</div>
              <div className="text-xs text-faint tabular-nums">
                {stop.completed}/{stop.total} steps
              </div>
            </div>
            <ArrowRight size={14} className="ml-auto shrink-0 text-faint" />
          </Link>
        </li>
      ))}
    </ol>
  )
}

function StopBadge({ index, stop, here, className }) {
  return (
    <span
      className={cn(
        'grid place-items-center rounded-full font-display font-bold text-white transition-transform group-hover:scale-110',
        here && 'outline-4 outline-offset-4 outline-accent',
        className,
      )}
      style={{ background: stop.category.color }}
    >
      {index + 1}
    </span>
  )
}
