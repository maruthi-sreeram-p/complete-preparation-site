import { useMemo, useState } from 'react'
import { Link, NavLink, useNavigate, useParams } from 'react-router-dom'
import { Database, ExternalLink, ListChecks, Table2 } from 'lucide-react'
import NotFound from '@/components/layout/NotFound.jsx'
import ProgressBar from '@/components/ui/ProgressBar.jsx'
import Markdown from '@/features/content/blocks/Markdown.jsx'
import CustomProblems from './CustomProblems.jsx'
import QuestionCard, { ResultTable } from './QuestionCard.jsx'
import { usePractice } from './PracticeProvider.jsx'
import { getSubject, groupSubjects, listSubjects } from '@/lib/practice/registry.js'
import { isDone, overallStats, subjectStats } from '@/lib/practice/state.js'
import { loadSqlEngine, runQuery } from '@/lib/practice/sql.js'
import { cn, paths } from '@/lib/util.js'

export default function PracticePage() {
  const { subjectId } = useParams()
  const subjects = listSubjects()
  const subject = subjectId ? getSubject(subjectId) : null
  if (subjectId && !subject) return <NotFound message={`There is no practice subject called "${subjectId}".`} />

  return (
    <div className="mx-auto grid max-w-7xl gap-8 px-4 py-8 lg:grid-cols-[17rem_minmax(0,1fr)] lg:px-6 lg:py-10">
      <Sidebar subjects={subjects} activeId={subject?.id} />
      <div className="min-w-0">{subject ? <SubjectView key={subject.id} subject={subject} /> : <Overview subjects={subjects} />}</div>
    </div>
  )
}

function Sidebar({ subjects, activeId }) {
  const navigate = useNavigate()
  const { state } = usePractice()
  const groups = useMemo(() => groupSubjects(subjects), [subjects])
  return (
    <aside className="lg:sticky lg:top-20 lg:self-start">
      {/* small screens: a select is easier than a long list */}
      <select
        value={activeId ?? ''}
        onChange={(e) => navigate(paths.practice(e.target.value))}
        aria-label="Practice subject"
        className="w-full rounded-lg border border-line bg-panel px-3 py-2 text-sm lg:hidden"
      >
        <option value="">All subjects</option>
        {groups.map((g) => (
          <optgroup key={g.name} label={g.name}>
            {g.subjects.map((s) => (
              <option key={s.id} value={s.id}>
                {s.title}
              </option>
            ))}
          </optgroup>
        ))}
      </select>

      <nav aria-label="Practice subjects" className="hidden max-h-[calc(100dvh-7rem)] space-y-5 overflow-y-auto pr-1 lg:block">
        <NavLink to={paths.practice()} end className={({ isActive }) => sideLink(isActive)}>
          <ListChecks size={15} /> All subjects
        </NavLink>
        {groups.map((g) => (
          <div key={g.name}>
            <p className="px-3 pb-1.5 text-[11px] font-semibold tracking-wider text-faint uppercase">{g.name}</p>
            <ul className="space-y-0.5">
              {g.subjects.map((s) => {
                const st = subjectStats(s, state)
                return (
                  <li key={s.id}>
                    <NavLink to={paths.practice(s.id)} className={({ isActive }) => sideLink(isActive)}>
                      <span className="min-w-0 flex-1 truncate">{s.title}</span>
                      <span className="shrink-0 text-xs tabular-nums text-faint">
                        {st.done}/{st.total}
                      </span>
                    </NavLink>
                  </li>
                )
              })}
            </ul>
          </div>
        ))}
      </nav>
    </aside>
  )
}

const sideLink = (active) =>
  cn(
    'flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors',
    active ? 'bg-panel-2 font-medium text-ink' : 'text-muted hover:bg-panel hover:text-ink',
  )

function Overview({ subjects }) {
  const { state } = usePractice()
  const groups = useMemo(() => groupSubjects(subjects), [subjects])
  const total = overallStats(subjects, state)
  return (
    <div>
      <h1 className="font-display text-3xl font-bold tracking-tight">Practice</h1>
      <p className="mt-2 max-w-2xl text-muted">
        Pick a subject and work through its questions. Write SQL and run it on a real database, write short answers and
        compare them with a model answer, or open problems on LeetCode and other platforms and tick them off here.
        Everything you write is saved in this browser.
      </p>
      <div className="mt-5 flex max-w-md items-center gap-3">
        <ProgressBar value={total.percent} />
        <span className="shrink-0 text-sm tabular-nums text-muted">
          {total.done} / {total.total} done
        </span>
      </div>

      {groups.map((g) => (
        <section key={g.name} className="mt-9">
          <h2 className="mb-3 text-sm font-semibold tracking-wider text-faint uppercase">{g.name}</h2>
          <ul className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {g.subjects.map((s) => {
              const st = subjectStats(s, state)
              const kinds = [...new Set(s.questions.map((q) => (q.type === 'sql' ? 'SQL' : q.type === 'coding' ? 'Problems' : 'Written')))]
              return (
                <li key={s.id}>
                  <Link to={paths.practice(s.id)} className="flex h-full flex-col rounded-xl border border-line bg-panel p-4 transition-colors hover:border-accent">
                    <span className="font-medium">{s.title}</span>
                    <span className="mt-1 line-clamp-2 text-sm text-muted">{s.description}</span>
                    <span className="mt-3 flex items-center justify-between text-xs text-faint">
                      <span>{kinds.join(' · ')}</span>
                      <span className="tabular-nums">
                        {st.done}/{st.total}
                      </span>
                    </span>
                    <ProgressBar value={st.percent} className="mt-2" />
                  </Link>
                </li>
              )
            })}
          </ul>
        </section>
      ))}
    </div>
  )
}

const LEVELS = ['Easy', 'Medium', 'Hard']
const KIND_LABEL = { sql: 'SQL', written: 'Theory', coding: 'Problems' }

function Chips({ options, value, onChange, label }) {
  return (
    <div className="flex flex-wrap items-center gap-1.5" role="group" aria-label={label}>
      {options.map(([key, text]) => (
        <button
          key={key}
          type="button"
          onClick={() => onChange(key)}
          aria-pressed={value === key}
          className={cn(
            'rounded-full border px-3 py-1 text-xs font-medium transition-colors',
            value === key ? 'border-accent bg-accent/15 text-ink' : 'border-line text-muted hover:border-line-strong hover:text-ink',
          )}
        >
          {text}
        </button>
      ))}
    </div>
  )
}

function SubjectView({ subject }) {
  const { state } = usePractice()
  const stats = subjectStats(subject, state)
  const [level, setLevel] = useState('all')
  const [kind, setKind] = useState('all')
  const [status, setStatus] = useState('all')

  const levelsPresent = LEVELS.filter((l) => subject.questions.some((q) => q.level === l))
  const kindsPresent = [...new Set(subject.questions.map((q) => q.type ?? 'written'))]

  const visible = subject.questions
    .map((q, i) => ({ q, number: i + 1 }))
    .filter(({ q }) => (level === 'all' || q.level === level) && (kind === 'all' || (q.type ?? 'written') === kind))
    .filter(({ q }) => status === 'all' || (status === 'done') === isDone(state, q.id))

  return (
    <div>
      <p className="text-xs font-semibold tracking-wider text-faint uppercase">{subject.group}</p>
      <h1 className="mt-1 font-display text-3xl font-bold tracking-tight">{subject.title}</h1>
      {subject.description && <p className="mt-2 max-w-3xl text-muted">{subject.description}</p>}
      <div className="mt-4 flex max-w-md items-center gap-3">
        <ProgressBar value={stats.percent} />
        <span className="shrink-0 text-sm tabular-nums text-muted">
          {stats.done} / {stats.total} done
        </span>
      </div>

      {subject.platforms.length > 0 && (
        <div className="mt-5">
          <p className="mb-2 text-xs font-semibold tracking-wider text-faint uppercase">Practise this elsewhere</p>
          <ul className="flex flex-wrap gap-2">
            {subject.platforms.map((p) => (
              <li key={p.url}>
                <a
                  href={p.url}
                  target="_blank"
                  rel="noreferrer noopener"
                  title={p.note}
                  className="inline-flex items-center gap-1.5 rounded-full border border-line-strong bg-panel px-3.5 py-1.5 text-sm transition-colors hover:border-accent"
                >
                  {p.name} <ExternalLink size={13} className="text-faint" />
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}

      {subject.dataset && <DatasetExplorer dataset={subject.dataset} />}

      <div className="mt-8 flex flex-wrap items-center gap-x-6 gap-y-3">
        {kindsPresent.length > 1 && (
          <Chips label="Question type" value={kind} onChange={setKind} options={[['all', 'All'], ...kindsPresent.map((k) => [k, KIND_LABEL[k] ?? k])]} />
        )}
        {levelsPresent.length > 1 && (
          <Chips label="Level" value={level} onChange={setLevel} options={[['all', 'Any level'], ...levelsPresent.map((l) => [l, l])]} />
        )}
        <Chips label="Status" value={status} onChange={setStatus} options={[['all', 'All'], ['todo', 'To do'], ['done', 'Done']]} />
      </div>

      <ol className="mt-4 space-y-3" aria-label="Questions">
        {visible.map(({ q, number }) => (
          <QuestionCard key={q.id} question={q} index={number} subject={subject} />
        ))}
      </ol>
      {visible.length === 0 && <p className="mt-6 rounded-xl border border-dashed border-line p-6 text-center text-sm text-muted">No questions match these filters.</p>}

      <CustomProblems subject={subject} />
    </div>
  )
}

/** Lets the learner look at the tables before writing a query against them. */
function DatasetExplorer({ dataset }) {
  const tables = useMemo(() => [...dataset.sql.matchAll(/CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?"?(\w+)"?/gi)].map((m) => m[1]), [dataset])
  const [selected, setSelected] = useState(null)
  const [result, setResult] = useState(null)

  const open = async (table) => {
    setSelected(table)
    setResult({ loading: true })
    try {
      const SQL = await loadSqlEngine()
      setResult(runQuery(SQL, dataset.sql, `SELECT * FROM ${table} LIMIT 25`))
    } catch (error) {
      setResult({ ok: false, error: `The SQL engine could not be loaded (${error.message}).` })
    }
  }

  return (
    <details className="mt-6 rounded-xl border border-line bg-panel p-4" open>
      <summary className="flex cursor-pointer items-center gap-2 font-medium">
        <Database size={16} className="text-accent" /> {dataset.title ?? 'Practice database'}
      </summary>
      {dataset.description && (
        <div className="mt-3 text-sm">
          <Markdown>{dataset.description}</Markdown>
        </div>
      )}
      <p className="mt-3 text-xs text-muted">
        Queries run on a SQLite database inside your browser, rebuilt from scratch for every run, so you cannot break it. Click a table to see its rows.
      </p>
      <div className="mt-2 flex flex-wrap gap-2">
        {tables.map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => open(t)}
            aria-pressed={selected === t}
            className={cn(
              'inline-flex items-center gap-1.5 rounded-full border px-3 py-1 font-mono text-xs transition-colors',
              selected === t ? 'border-accent bg-accent/15 text-ink' : 'border-line text-muted hover:border-line-strong hover:text-ink',
            )}
          >
            <Table2 size={12} /> {t}
          </button>
        ))}
      </div>
      {result?.loading && <p className="mt-3 text-xs text-muted">Loading…</p>}
      {result && !result.loading && !result.ok && <p className="mt-3 font-mono text-xs text-danger">{result.error}</p>}
      {result?.ok && result.columns.length > 0 && (
        <div className="mt-3">
          <ResultTable columns={result.columns} rows={result.rows} />
        </div>
      )}
    </details>
  )
}
