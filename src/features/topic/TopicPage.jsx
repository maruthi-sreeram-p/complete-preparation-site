import { useEffect, useState } from 'react'
import { Link, useLocation, useParams } from 'react-router-dom'
import { ArrowLeft, ArrowRight, CalendarDays, Clock, FileText, Lock } from 'lucide-react'
import { useRoadmapScope } from '@/features/roadmap/RoadmapScope.jsx'
import { useTopicContent } from './useTopicContent.js'
import ContentRenderer from '@/features/content/ContentRenderer.jsx'
import { sectionMeta } from '@/features/content/sectionTypes.js'
import { TopicChips } from '@/features/content/blocks/SimpleBlocks.jsx'
import StatusSelect from '@/components/ui/StatusSelect.jsx'
import StatusIcon from '@/components/ui/StatusIcon.jsx'
import CategoryBadge from '@/components/ui/CategoryBadge.jsx'
import NotFound from '@/components/layout/NotFound.jsx'
import { STATUS, nextStatus } from '@/lib/progress/status.js'
import { cn, paths } from '@/lib/util.js'

export default function TopicPage() {
  const { topicId } = useParams()
  const scope = useRoadmapScope()
  const topic = scope.roadmap.topicsById[topicId]
  if (!topic) return <NotFound message={`There is no topic called "${topicId}" in this roadmap.`} />
  return <Topic key={topic.id} topic={topic} scope={scope} />
}

function Topic({ topic, scope }) {
  const { roadmap, statusOf, setTopicStatus, markStudied } = scope
  const category = roadmap.categoryById[topic.categoryId]
  const status = statusOf(topic.id)
  const result = useTopicContent(roadmap.id, topic)
  const { hash } = useLocation()

  // a link like .../topics/<id>#ch-6-8 jumps to that section once the content has loaded
  useEffect(() => {
    if (result.status !== 'ready' || !hash) return
    document.getElementById(decodeURIComponent(hash.slice(1)))?.scrollIntoView()
  }, [result.status, hash])

  useEffect(() => {
    window.scrollTo(0, 0)
    markStudied(topic.id)
    // markStudied changes identity with progress; only record a visit when the topic changes.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [topic.id])

  const sections = result.status === 'ready' ? result.content.sections : []
  const prerequisites = topic.requires.map((id) => roadmap.topicsById[id])
  const unlocks = roadmap.unlocks[topic.id].map((id) => roadmap.topicsById[id])
  const source = result.content?.source ?? topic.source

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 lg:grid lg:grid-cols-[14rem_minmax(0,1fr)] lg:gap-10">
      <aside className="hidden lg:block">
        <div className="sticky top-20 space-y-6">
          <Link
            to={paths.roadmap(roadmap.id)}
            className="inline-flex items-center gap-1.5 text-sm text-muted transition-colors hover:text-ink"
          >
            <ArrowLeft size={14} /> Roadmap
          </Link>
          {sections.length > 0 && <SectionToc sections={sections} />}
        </div>
      </aside>

      <article className="min-w-0 max-w-3xl">
        <Link to={paths.roadmap(roadmap.id)} className="mb-4 inline-flex items-center gap-1.5 text-sm text-muted hover:text-ink lg:hidden">
          <ArrowLeft size={14} /> Roadmap
        </Link>

        <header className="space-y-4">
          <CategoryBadge category={category} />
          <h1 className="text-3xl font-semibold tracking-tight">{topic.title}</h1>
          {topic.summary && <p className="text-muted">{topic.summary}</p>}
          <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-faint">
            {topic.estimatedMinutes && (
              <span className="inline-flex items-center gap-1">
                <Clock size={13} /> {topic.estimatedMinutes} min
              </span>
            )}
            {source?.planDays && (
              <span className="inline-flex items-center gap-1">
                <CalendarDays size={13} /> Plan day{/[,–]/.test(source.planDays) ? 's' : ''} {source.planDays}
              </span>
            )}
            {source?.document && (
              <span className="inline-flex items-center gap-1">
                <FileText size={13} /> {source.document}
                {source.pages && ` · pp. ${source.pages}`}
              </span>
            )}
          </div>
          <StatusSelect value={status} onChange={(s) => setTopicStatus(topic.id, s)} />
        </header>

        {topic.subtopics.length > 0 && <SubtopicChecklist topic={topic} scope={scope} sections={sections} />}

        {prerequisites.length > 0 && (
          <div className="mt-6">
            <h2 className="mb-2 flex items-center gap-1.5 text-xs font-medium uppercase tracking-wider text-faint">
              <Lock size={11} /> Prerequisites
            </h2>
            <TopicChips topics={prerequisites} roadmapId={roadmap.id} statusOf={statusOf} />
          </div>
        )}

        <hr className="my-8 border-line" />

        {result.status === 'loading' && <p className="py-10 text-sm text-faint">Loading…</p>}
        {result.status === 'error' && (
          <div className="rounded-xl border border-danger/30 bg-danger/5 p-4 text-sm">
            <div className="font-medium text-danger">This topic's content could not be loaded.</div>
            <div className="mt-1 text-muted">{String(result.error?.message ?? result.error)}</div>
          </div>
        )}
        {result.status === 'missing' && (
          <div className="rounded-xl border border-dashed border-line-strong p-8 text-center">
            <div className="font-medium">No content for this topic yet</div>
            <p className="mt-1 text-sm text-muted">
              Add{' '}
              <code className="rounded bg-panel-2 px-1.5 py-0.5 font-mono text-xs">
                content/roadmaps/{roadmap.id}/topics/{topic.contentId}.json
              </code>{' '}
              to fill this page.
            </p>
          </div>
        )}
        {result.status === 'ready' && <ContentRenderer content={result.content} />}

        {unlocks.length > 0 && (
          <div className="mt-12">
            <h2 className="mb-2 text-xs font-medium uppercase tracking-wider text-faint">Unlocks</h2>
            <TopicChips topics={unlocks} roadmapId={roadmap.id} statusOf={statusOf} />
          </div>
        )}

        <TopicPager topic={topic} scope={scope} />
      </article>
    </div>
  )
}

function SubtopicChecklist({ topic, scope, sections }) {
  const { subStatusOf, setSubtopicStatus, subProgress } = scope
  const { done, total } = subProgress(topic.id)
  const sectionFor = (subId) => sections.find((s) => s.subtopicId === subId)

  return (
    <div className="mt-6 rounded-xl border border-line bg-panel p-4">
      <div className="mb-2 flex items-center justify-between text-xs">
        <span className="font-medium uppercase tracking-wider text-faint">Subtopics</span>
        <span className="tabular-nums text-muted">
          {done}/{total}
        </span>
      </div>
      <ul className="space-y-0.5">
        {topic.subtopics.map((sub) => {
          const status = subStatusOf(topic.id, sub.id)
          const section = sectionFor(sub.id)
          return (
            <li key={sub.id} className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setSubtopicStatus(topic.id, sub.id, nextStatus(status))}
                aria-label={`${sub.title}: ${status}. Click to change.`}
                className="rounded-full p-1.5 transition-transform hover:scale-110"
              >
                <StatusIcon status={status} size={17} />
              </button>
              {sub.pages && <span className="order-last ml-auto text-[11px] tabular-nums text-faint">pp. {sub.pages}</span>}
              {section ? (
                <a
                  href={`#${section.id}`}
                  onClick={(e) => {
                    e.preventDefault()
                    document.getElementById(section.id)?.scrollIntoView({ behavior: 'smooth' })
                  }}
                  className={cn('text-sm hover:text-accent', status === STATUS.COMPLETED && 'text-muted line-through')}
                >
                  {sub.title}
                </a>
              ) : (
                <span className={cn('text-sm', status === STATUS.COMPLETED && 'text-muted line-through')}>
                  {sub.title}
                </span>
              )}
            </li>
          )
        })}
      </ul>
    </div>
  )
}

function SectionToc({ sections }) {
  const [active, setActive] = useState(sections[0]?.id)

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries.filter((e) => e.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)
        if (visible[0]) setActive(visible[0].target.id)
      },
      { rootMargin: '-80px 0px -65% 0px' },
    )
    sections.forEach((s) => {
      const el = document.getElementById(s.id)
      if (el) observer.observe(el)
    })
    return () => observer.disconnect()
  }, [sections])

  return (
    <nav aria-label="On this page">
      <div className="mb-2 text-xs font-medium uppercase tracking-wider text-faint">On this page</div>
      <ul className="space-y-0.5 border-l border-line">
        {sections.map((section) => {
          const { label } = sectionMeta(section.type)
          const on = active === section.id
          return (
            <li key={section.id}>
              <a
                href={`#${section.id}`}
                onClick={(e) => {
                  e.preventDefault()
                  document.getElementById(section.id)?.scrollIntoView({ behavior: 'smooth' })
                }}
                className={cn(
                  '-ml-px block border-l py-1 pl-3 text-[13px] transition-colors',
                  on ? 'border-accent text-ink' : 'border-transparent text-muted hover:text-ink',
                )}
              >
                {section.title || label}
              </a>
            </li>
          )
        })}
      </ul>
    </nav>
  )
}

function TopicPager({ topic, scope }) {
  const { roadmap, statusOf, setTopicStatus } = scope
  const index = roadmap.sequence.indexOf(topic.id)
  const prev = roadmap.topicsById[roadmap.sequence[index - 1]]
  const next = roadmap.topicsById[roadmap.sequence[index + 1]]
  const status = statusOf(topic.id)

  return (
    <nav aria-label="Topic navigation" className="mt-12 grid gap-3 border-t border-line pt-6 sm:grid-cols-2">
      {prev ? (
        <Link
          to={paths.topic(roadmap.id, prev.id)}
          className="rounded-xl border border-line bg-panel p-4 transition-colors hover:border-line-strong"
        >
          <div className="mb-1 flex items-center gap-1.5 text-xs text-faint">
            <ArrowLeft size={12} /> Previous
          </div>
          <div className="truncate text-sm font-medium">{prev.title}</div>
        </Link>
      ) : (
        <span />
      )}
      {next && (
        <Link
          to={paths.topic(roadmap.id, next.id)}
          onClick={() => status !== STATUS.COMPLETED && setTopicStatus(topic.id, STATUS.COMPLETED)}
          className="rounded-xl border border-line bg-panel p-4 text-right transition-colors hover:border-accent/50"
        >
          <div className="mb-1 flex items-center justify-end gap-1.5 text-xs text-faint">
            {status === STATUS.COMPLETED ? 'Next' : 'Complete and continue'} <ArrowRight size={12} />
          </div>
          <div className="truncate text-sm font-medium">{next.title}</div>
        </Link>
      )}
    </nav>
  )
}
