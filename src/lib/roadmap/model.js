import { resolveCategoryColor } from './colors.js'

/**
 * Roadmap data model.
 *
 * `buildRoadmap` turns the raw roadmap.json supplied by the user into a validated,
 * indexed model. It never throws on bad data: problems are collected in `issues`
 * (and the offending entries are dropped) so the UI keeps working and can show them.
 *
 * Raw shape (see content/README.md):
 *   { title, description?, placeholder?,
 *     categories: [{ id, title, description?, color? }],
 *     topics: [{ id, title, category, summary?, requires?: [topicId],
 *                subtopics?: [{ id, title }], contentId?, estimatedMinutes?,
 *                position?: { x, y }, source?: {...} }] }
 *
 * @typedef {{ id: string, title: string, pages?: string }} Subtopic
 * @typedef {{
 *   id: string, title: string, summary: string, categoryId: string,
 *   requires: string[], subtopics: Subtopic[], contentId: string, hasContent: boolean,
 *   estimatedMinutes?: number, position?: {x:number,y:number}, source?: object, order: number
 * }} Topic
 */

export const UNCATEGORIZED_ID = 'uncategorized'

const isNonEmptyString = (v) => typeof v === 'string' && v.trim() !== ''

/**
 * @param {object} raw parsed roadmap.json
 * @param {{ id: string, contentIds?: Set<string> }} options
 */
export function buildRoadmap(raw, { id, contentIds = new Set() }) {
  const issues = []
  const error = (message) => issues.push({ level: 'error', message })
  const warn = (message) => issues.push({ level: 'warning', message })

  const rawCategories = Array.isArray(raw?.categories) ? raw.categories : []
  const rawTopics = Array.isArray(raw?.topics) ? raw.topics : []

  // ---- categories
  const categories = []
  const categoryById = {}
  const addCategory = (c) => {
    const category = {
      id: c.id,
      title: isNonEmptyString(c.title) ? c.title : c.id,
      description: typeof c.description === 'string' ? c.description : '',
      color: resolveCategoryColor(c.color, categories.length),
    }
    categories.push(category)
    categoryById[category.id] = category
  }
  for (const c of rawCategories) {
    if (!c || !isNonEmptyString(c.id)) {
      error('A category without an id was ignored.')
      continue
    }
    if (categoryById[c.id]) {
      warn(`Duplicate category id "${c.id}" was ignored.`)
      continue
    }
    addCategory(c)
  }
  const ensureUncategorized = () => {
    if (!categoryById[UNCATEGORIZED_ID]) {
      addCategory({ id: UNCATEGORIZED_ID, title: 'Uncategorized', color: '#6c7290' })
    }
    return UNCATEGORIZED_ID
  }

  // ---- topics
  /** @type {Topic[]} */
  const topics = []
  const topicsById = {}
  const rawRequires = {}
  rawTopics.forEach((t, index) => {
    if (!t || !isNonEmptyString(t.id)) {
      error(`Topic #${index + 1} has no id and was ignored.`)
      return
    }
    if (topicsById[t.id]) {
      error(`Duplicate topic id "${t.id}" was ignored.`)
      return
    }

    let categoryId = t.category
    if (!categoryId || !categoryById[categoryId]) {
      if (categoryId) warn(`Topic "${t.id}" uses unknown category "${categoryId}".`)
      categoryId = ensureUncategorized()
    }

    const subtopics = []
    const seenSubs = new Set()
    for (const s of Array.isArray(t.subtopics) ? t.subtopics : []) {
      if (!s || !isNonEmptyString(s.id)) {
        warn(`Topic "${t.id}" has a subtopic without an id; it was ignored.`)
        continue
      }
      if (seenSubs.has(s.id)) {
        warn(`Topic "${t.id}" repeats subtopic id "${s.id}"; the repeat was ignored.`)
        continue
      }
      seenSubs.add(s.id)
      subtopics.push({
        id: s.id,
        title: isNonEmptyString(s.title) ? s.title : s.id,
        pages: isNonEmptyString(s.pages) ? s.pages : undefined,
      })
    }

    const contentId = isNonEmptyString(t.contentId) ? t.contentId : t.id
    const pos = t.position
    const topic = {
      id: t.id,
      title: isNonEmptyString(t.title) ? t.title : t.id,
      summary: typeof t.summary === 'string' ? t.summary : '',
      categoryId,
      requires: [],
      subtopics,
      contentId,
      hasContent: contentIds.has(contentId),
      estimatedMinutes: Number.isFinite(t.estimatedMinutes) ? t.estimatedMinutes : undefined,
      position:
        pos && Number.isFinite(pos.x) && Number.isFinite(pos.y) ? { x: pos.x, y: pos.y } : undefined,
      source: t.source && typeof t.source === 'object' ? t.source : undefined,
      order: topics.length,
    }
    topics.push(topic)
    topicsById[topic.id] = topic
    rawRequires[topic.id] = Array.isArray(t.requires) ? t.requires : []
  })

  if (topics.length === 0) warn('The roadmap has no topics.')

  // ---- dependencies
  for (const topic of topics) {
    const seen = new Set()
    for (const reqId of rawRequires[topic.id]) {
      if (reqId === topic.id) {
        warn(`Topic "${topic.id}" requires itself; the dependency was ignored.`)
      } else if (!topicsById[reqId]) {
        warn(`Topic "${topic.id}" requires unknown topic "${reqId}"; the dependency was ignored.`)
      } else if (!seen.has(reqId)) {
        seen.add(reqId)
        topic.requires.push(reqId)
      }
    }
  }

  breakCycles(topics, topicsById, error)

  // ---- derived structures
  const unlocks = {}
  for (const topic of topics) unlocks[topic.id] = []
  const edges = []
  for (const topic of topics) {
    for (const reqId of topic.requires) {
      unlocks[reqId].push(topic.id)
      edges.push({ id: `${reqId}->${topic.id}`, source: reqId, target: topic.id })
    }
  }

  return {
    id,
    title: isNonEmptyString(raw?.title) ? raw.title : id,
    description: typeof raw?.description === 'string' ? raw.description : '',
    placeholder: raw?.placeholder === true,
    layout: raw?.layout === 'tree' ? 'tree' : 'layered',
    categories,
    categoryById,
    topics,
    topicsById,
    edges,
    unlocks,
    sequence: learningSequence(topics),
    issues,
  }
}

/** Drop the dependency that closes each cycle (depth-first, in topic order). */
function breakCycles(topics, topicsById, error) {
  const WHITE = 0, GRAY = 1, BLACK = 2
  const color = {}
  const visit = (topic) => {
    color[topic.id] = GRAY
    for (const reqId of [...topic.requires]) {
      const state = color[reqId] ?? WHITE
      if (state === GRAY) {
        topic.requires = topic.requires.filter((r) => r !== reqId)
        error(`Dependency cycle: "${topic.id}" requires "${reqId}", which depends on it. That dependency was ignored.`)
      } else if (state === WHITE) {
        visit(topicsById[reqId])
      }
    }
    color[topic.id] = BLACK
  }
  for (const topic of topics) if ((color[topic.id] ?? WHITE) === WHITE) visit(topic)
}

/**
 * Learning sequence: a topological order of the dependency graph that, among
 * topics that are ready at the same time, follows the order in roadmap.json.
 */
function learningSequence(topics) {
  const remaining = new Map(topics.map((t) => [t.id, t.requires.length]))
  const dependents = {}
  for (const t of topics) for (const r of t.requires) (dependents[r] ??= []).push(t.id)
  const done = new Set()
  const sequence = []
  while (sequence.length < topics.length) {
    const next = topics.find((t) => !done.has(t.id) && remaining.get(t.id) === 0)
    if (!next) break // unreachable once cycles are broken
    done.add(next.id)
    sequence.push(next.id)
    for (const d of dependents[next.id] ?? []) remaining.set(d, remaining.get(d) - 1)
  }
  return sequence
}

/** All transitive prerequisites of a topic. */
export function ancestorsOf(roadmap, topicId) {
  return walk(topicId, (id) => roadmap.topicsById[id].requires)
}

/** All topics that transitively depend on a topic. */
export function descendantsOf(roadmap, topicId) {
  return walk(topicId, (id) => roadmap.unlocks[id])
}

function walk(startId, neighbours) {
  const found = new Set()
  const stack = [...neighbours(startId)]
  while (stack.length) {
    const id = stack.pop()
    if (found.has(id)) continue
    found.add(id)
    stack.push(...neighbours(id))
  }
  return found
}
