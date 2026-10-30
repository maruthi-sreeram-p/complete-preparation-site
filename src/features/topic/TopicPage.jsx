import { useEffect, useMemo } from 'react'
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, ArrowRight, CalendarDays, Check, Clock, FileText, ListTree, Lock } from 'lucide-react'
import { useRoadmapScope } from '@/features/roadmap/RoadmapScope.jsx'
import { useTopicContent } from './useTopicContent.js'
import { Section } from '@/features/content/ContentRenderer.jsx'
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
  const { roadmap, statusOf, setTopicStatus, markStudied, subStatusOf } = scope
  const category = roadmap.categoryById[topic.categoryId]
  const status = statusOf(topic.id)
  const result = useTopicContent(roadmap.id, topic)
  const { hash } = useLocation()
  const navigate = useNavigate()

  useEffect(() => {
    window.scrollTo(0, 0)
    markStudied(topic.id)
    // markStudied changes identity with progress; only record a visit when the topic changes.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [topic.id])

  const sections = useMemo(() => (result.status === 'ready' ? result.content.sections : []), [result])
  // Long parts are read one chapter at a time, which keeps very large pages responsive.
  const paged = sections.some((s) => s.subtopicId)
  const hashId = decodeURIComponent(hash.slice(1))

  const activeId = useMemo(() => {
    if (!paged) return null
    if (sections.some((s) => s.id === hashId)) return hashId
    const firstOpen = sections.find(
      (s) => s.subtopicId && subStatusOf(topic.id, s.subtopicId) !== STATUS.COMPLETED,
    )
    return (firstOpen ?? sections[0]).id
    // the default chapter is chosen once; ticking a chapter must not move the reader
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [paged, sections, hashId])

  useEffect(() => {
    if (result.status !== 'ready' || !hashId) return
    if (paged) window.scrollTo(0, 0)
    else document.getElementById(hashId)?.scrollIntoView()
  }, [result.status, hashId, paged])

  const openSection = (id) => navigate({ hash: `#${id}` })

  const activeIndex = sections.findIndex((s) => s.id === activeId)
  const active = sections[activeIndex]
  const step = roadmap.sequence.indexOf(topic.id) + 1
  const isTree = roadmap.layout === 'tree'
  const prerequisites = topic.requires.map((id) => roadmap.topicsById[id])
  const source = result.content?.source ?? topic.source
  const showTopicPager = !paged || activeIndex === sections.length - 1

  const nav = sections.length > 0 && (
    <ChapterNav
      topic={topic}
      scope={scope}
      sections={sections}
      activeId={activeId}
      onOpen={paged ? openSection : (id) => document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })}
    />
  )

  return (
    <div className="w-full px-4 py-8 lg:grid lg:grid-cols-[17rem_minmax(0,1fr)] lg:gap-8 lg:px-6">
      <aside className="hidden lg:block">
        <div className="sticky top-20 flex max-h-[calc(100dvh-6rem)] flex-col gap-4">
          <Link
            to={paths.roadmap(roadmap.id)}
            className="inline-flex items-center gap-1.5 text-sm text-muted transition-colors hover:text-ink"
          >
            <ArrowLeft size={14} /> Roadmap
          </Link>
          {nav}
        </div>
      </aside>

      <article className="min-w-0">
        <Link to={paths.roadmap(roadmap.id)} className="mb-4 inline-flex items-center gap-1.5 text-sm text-muted hover:text-ink lg:hidden">
          <ArrowLeft size={14} /> Roadmap
        </Link>

        <header className="space-y-4">
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
            {isTree && <span className="text-xs font-medium text-accent">Step {step} of {roadmap.sequence.length}</span>}
            <CategoryBadge category={category} />
          </div>
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

        {sections.length > 1 && (
          <details className="mt-6 rounded-xl border border-line bg-panel p-3 lg:hidden">
            <summary className="flex cursor-pointer items-center gap-2 text-sm text-muted">
              <ListTree size={15} /> Chapters
            </summary>
            <div className="mt-3">{nav}</div>
          </details>
        )}

        {!isTree && prerequisites.length > 0 && (
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

        {result.status === 'ready' && paged && active && (
          <>
            <Section key={active.id} section={active} />
            <ChapterPager
              topic={topic}
              scope={scope}
              sections={sections}
              index={activeIndex}
              onOpen={openSection}
            />
          </>
        )}
        {result.status === 'ready' && !paged && (
          <div className="space-y-12">
            {sections.map((section) => (
              <Section key={section.id} section={section} />
            ))}
          </div>
        )}

        {showTopicPager && <TopicPager topic={topic} scope={scope} />}
      </article>
    </div>
  )
}

/** The chapters of this part, with their status; the current one is highlighted. */
function ChapterNav({ topic, scope, sections, activeId, onOpen }) {
  const { subStatusOf, setSubtopicStatus, subProgress } = scope
  const { done, total } = subProgress(topic.id)
  const pagesOf = (subId) => topic.subtopics.find((s) => s.id === subId)?.pages

  return (
    <nav aria-label="Chapters" className="flex min-h-0 flex-col">
      <div className="mb-2 flex items-center justify-between text-xs">
        <span className="font-medium uppercase tracking-wider text-faint">
          {total > 0 ? 'Chapters' : 'On this page'}
        </span>
        {total > 0 && (
          <span className="tabular-nums text-muted">
            {done}/{total}
          </span>
        )}
      </div>
      <ul className="min-h-0 space-y-0.5 overflow-y-auto pr-1">
        {sections.map((section) => {
          const { label } = sectionMeta(section.type)
          const status = section.subtopicId ? subStatusOf(topic.id, section.subtopicId) : null
          const on = activeId === section.id
          const pages = section.subtopicId && pagesOf(section.subtopicId)
          return (
            <li key={section.id} className={cn('flex items-start gap-1 rounded-lg', on && 'bg-panel-2')}>
              {status ? (
                <button
                  type="button"
                  onClick={() => setSubtopicStatus(topic.id, section.subtopicId, nextStatus(status))}
                  aria-label={`${section.title}: ${status}. Click to change.`}
                  className="shrink-0 rounded-full p-1.5"
                >
                  <StatusIcon status={status} size={15} />
                </button>
              ) : (
                <span className="w-1.5 shrink-0" />
              )}
              <button
                type="button"
                onClick={() => onOpen(section.id)}
                title={pages ? `PDF pp. ${pages}` : undefined}
                className={cn(
                  'min-w-0 flex-1 py-1.5 pr-2 text-left text-[13px] leading-snug transition-colors',
                  on ? 'text-ink' : 'text-muted hover:text-ink',
                )}
              >
                {section.title || label}
              </button>
            </li>
          )
        })}
      </ul>
    </nav>
  )
}

/** Moves between the chapters of one part. */
function ChapterPager({ topic, scope, sections, index, onOpen }) {
  const { subStatusOf, setSubtopicStatus } = scope
  const section = sections[index]
  const prev = sections[index - 1]
  const next = sections[index + 1]
  const status = section.subtopicId ? subStatusOf(topic.id, section.subtopicId) : null
  const completed = status === STATUS.COMPLETED

  return (
    <nav aria-label="Chapter navigation" className="mt-12 flex flex-wrap items-center justify-between gap-3 border-t border-line pt-6">
      {prev ? (
        <button
          type="button"
          onClick={() => onOpen(prev.id)}
          className="inline-flex min-w-0 items-center gap-1.5 text-sm text-muted transition-colors hover:text-ink"
        >
          <ArrowLeft size={14} className="shrink-0" /> <span className="truncate">{prev.title}</span>
        </button>
      ) : (
        <span />
      )}
      <div className="flex flex-wrap items-center gap-2">
        {status && !completed && (
          <button
            type="button"
            onClick={() => {
              setSubtopicStatus(topic.id, section.subtopicId, STATUS.COMPLETED)
              if (next) onOpen(next.id)
            }}
            className="inline-flex items-center gap-1.5 rounded-lg bg-ink px-3 py-1.5 text-sm font-medium text-canvas"
          >
            <Check size={14} /> Mark complete{next ? ' and continue' : ''}
          </button>
        )}
        {next && (status === null || completed) && (
          <button
            type="button"
            onClick={() => onOpen(next.id)}
            className="inline-flex min-w-0 items-center gap-1.5 rounded-lg border border-line px-3 py-1.5 text-sm text-muted transition-colors hover:text-ink"
          >
            <span className="truncate">{next.title}</span> <ArrowRight size={14} className="shrink-0" />
          </button>
        )}
      </div>
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
    <nav aria-label="Topic navigation" className="mt-8 grid gap-3 border-t border-line pt-6 sm:grid-cols-2">
      {prev ? (
        <Link
          to={paths.topic(roadmap.id, prev.id)}
          className="rounded-xl border border-line bg-panel p-4 transition-colors hover:border-line-strong"
        >
          <div className="mb-1 flex items-center gap-1.5 text-xs text-faint">
            <ArrowLeft size={12} /> Previous step
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
            {status === STATUS.COMPLETED ? 'Next step' : 'Complete and go to next step'} <ArrowRight size={12} />
          </div>
          <div className="truncate text-sm font-medium">{next.title}</div>
        </Link>
      )}
    </nav>
  )
}
