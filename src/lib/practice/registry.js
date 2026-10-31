/**
 * Practice subjects, one JSON file each:
 *
 *   content/practice/<subjectId>.json
 *   { id, title, group, order, description,
 *     platforms?: [{ name, url, note? }],          // places to practise this subject elsewhere
 *     dataset?: { title, description?, sql },      // makes "sql" questions runnable
 *     questions: [{ id, type: 'written' | 'sql' | 'coding', title, level?, prompt, hint?,
 *                   answer?,                       // model answer, markdown (written)
 *                   solution?, ordered?,           // reference query and whether row order counts (sql)
 *                   links?: [{ platform, label, url, number?, premium? }] }] }   // coding
 *
 * Adding a subject is adding a file; no code changes are needed.
 */
const files = import.meta.glob('/content/practice/*.json', { eager: true, import: 'default' })

const isString = (v) => typeof v === 'string' && v.trim() !== ''

function clean(raw) {
  if (!raw || !isString(raw.id) || !isString(raw.title) || !Array.isArray(raw.questions)) return null
  const seen = new Set()
  const questions = raw.questions.filter((q) => {
    if (!q || !isString(q.id) || !isString(q.title) || seen.has(q.id)) return false
    seen.add(q.id)
    return true
  })
  return {
    id: raw.id,
    title: raw.title,
    group: isString(raw.group) ? raw.group : 'Other',
    order: Number.isFinite(raw.order) ? raw.order : 99,
    description: typeof raw.description === 'string' ? raw.description : '',
    platforms: Array.isArray(raw.platforms) ? raw.platforms.filter((p) => isString(p?.name) && isString(p?.url)) : [],
    dataset: raw.dataset && isString(raw.dataset.sql) ? raw.dataset : null,
    questions,
  }
}

const subjects = Object.values(files)
  .map(clean)
  .filter(Boolean)
  .sort((a, b) => a.order - b.order || a.title.localeCompare(b.title))

export const listSubjects = () => subjects
export const getSubject = (id) => subjects.find((s) => s.id === id) ?? null

/** Subjects grouped for the sidebar, keeping the order in which the groups first appear. */
export function groupSubjects(list = subjects) {
  const groups = []
  for (const subject of list) {
    let group = groups.find((g) => g.name === subject.group)
    if (!group) groups.push((group = { name: subject.group, subjects: [] }))
    group.subjects.push(subject)
  }
  return groups
}
