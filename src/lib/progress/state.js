import { STATUS, isStatus } from './status.js'

/**
 * Progress state: plain JSON, independent of React and of where it is stored.
 *
 * {
 *   version: 1,
 *   activeRoadmapId: string | null,
 *   roadmaps: {
 *     [roadmapId]: {
 *       topics:      { [topicId]: { status, updatedAt } },
 *       subtopics:   { [`${topicId}/${subtopicId}`]: { status, updatedAt } },
 *       lastStudied: { [topicId]: timestamp }
 *     }
 *   }
 * }
 *
 * Only non-default (not "not-started") statuses are stored. Entries for topics
 * that no longer exist in a roadmap are ignored, so roadmap data can change freely.
 * Every function below is pure: it returns a new state and never mutates its input.
 */

export const PROGRESS_VERSION = 1

export const emptyProgress = () => ({ version: PROGRESS_VERSION, activeRoadmapId: null, roadmaps: {} })
const emptyRoadmapProgress = () => ({ topics: {}, subtopics: {}, lastStudied: {} })

const isObject = (v) => v !== null && typeof v === 'object' && !Array.isArray(v)

export const subtopicKey = (topicId, subtopicId) => `${topicId}/${subtopicId}`

function sanitizeEntries(value) {
  const out = {}
  if (!isObject(value)) return out
  for (const [key, entry] of Object.entries(value)) {
    if (isObject(entry) && isStatus(entry.status) && entry.status !== STATUS.NOT_STARTED) {
      out[key] = { status: entry.status, updatedAt: Number.isFinite(entry.updatedAt) ? entry.updatedAt : 0 }
    }
  }
  return out
}

/** Validate anything read from storage; unknown or corrupt data becomes empty progress. */
export function sanitizeProgress(value) {
  if (!isObject(value) || value.version !== PROGRESS_VERSION || !isObject(value.roadmaps)) {
    return emptyProgress()
  }
  const roadmaps = {}
  for (const [id, rp] of Object.entries(value.roadmaps)) {
    if (!isObject(rp)) continue
    const lastStudied = {}
    if (isObject(rp.lastStudied)) {
      for (const [topicId, ts] of Object.entries(rp.lastStudied)) {
        if (Number.isFinite(ts)) lastStudied[topicId] = ts
      }
    }
    roadmaps[id] = {
      topics: sanitizeEntries(rp.topics),
      subtopics: sanitizeEntries(rp.subtopics),
      lastStudied,
    }
  }
  return {
    version: PROGRESS_VERSION,
    activeRoadmapId: typeof value.activeRoadmapId === 'string' ? value.activeRoadmapId : null,
    roadmaps,
  }
}

// ---------- reads

export const statusOfTopic = (rp, topicId) => rp?.topics[topicId]?.status ?? STATUS.NOT_STARTED

export const statusOfSubtopic = (rp, topicId, subtopicId) =>
  rp?.subtopics[subtopicKey(topicId, subtopicId)]?.status ?? STATUS.NOT_STARTED

export function subtopicProgress(topic, rp) {
  const total = topic.subtopics.length
  const done = topic.subtopics.filter((s) => statusOfSubtopic(rp, topic.id, s.id) === STATUS.COMPLETED).length
  return { done, total }
}

const percent = (done, total) => (total === 0 ? 0 : Math.round((done / total) * 100))

export function computeStats(roadmap, rp) {
  const count = (topics) => {
    let completed = 0
    let inProgress = 0
    for (const t of topics) {
      const status = statusOfTopic(rp, t.id)
      if (status === STATUS.COMPLETED) completed++
      else if (status === STATUS.IN_PROGRESS) inProgress++
    }
    return { total: topics.length, completed, inProgress, notStarted: topics.length - completed - inProgress }
  }

  const overall = count(roadmap.topics)
  let subDone = 0
  let subTotal = 0
  for (const t of roadmap.topics) {
    const sp = subtopicProgress(t, rp)
    subDone += sp.done
    subTotal += sp.total
  }

  return {
    ...overall,
    percent: percent(overall.completed, overall.total),
    subtopics: { done: subDone, total: subTotal },
    byCategory: roadmap.categories
      .map((category) => {
        const c = count(roadmap.topics.filter((t) => t.categoryId === category.id))
        return { category, ...c, percent: percent(c.completed, c.total) }
      })
      .filter((c) => c.total > 0),
  }
}

/** Topics ordered by when they were last studied, newest first. */
export function recentTopics(roadmap, rp, limit = 8) {
  return roadmap.topics
    .filter((t) => rp?.lastStudied[t.id])
    .sort((a, b) => rp.lastStudied[b.id] - rp.lastStudied[a.id])
    .slice(0, limit)
}

/**
 * What "Continue learning" points at:
 *  1. the most recently studied topic that is not completed → resume
 *  2. else the first topic in the learning sequence whose prerequisites are all completed → next
 *  3. else the first unfinished topic in the sequence → next
 *  4. else null (everything is completed)
 */
export function pickContinueTarget(roadmap, rp) {
  const unfinished = roadmap.sequence
    .map((id) => roadmap.topicsById[id])
    .filter((t) => statusOfTopic(rp, t.id) !== STATUS.COMPLETED)
  if (unfinished.length === 0) return null

  const resume = recentTopics(roadmap, rp, roadmap.topics.length).find(
    (t) => statusOfTopic(rp, t.id) !== STATUS.COMPLETED,
  )
  if (resume) return { topic: resume, reason: 'resume' }

  const ready = unfinished.find((t) => t.requires.every((r) => statusOfTopic(rp, r) === STATUS.COMPLETED))
  return { topic: ready ?? unfinished[0], reason: 'next' }
}

// ---------- writes

function updateRoadmap(state, roadmapId, fn) {
  const current = state.roadmaps[roadmapId] ?? emptyRoadmapProgress()
  return { ...state, roadmaps: { ...state.roadmaps, [roadmapId]: fn(current) } }
}

function writeStatus(entries, key, status, now) {
  if (status === STATUS.NOT_STARTED) delete entries[key]
  else entries[key] = { status, updatedAt: now }
}

/**
 * Set a topic's status.
 * "Completed" and "Not started" also apply to every subtopic; "In progress" leaves them alone.
 */
export function setTopicStatus(state, roadmap, topicId, status, now = Date.now()) {
  const topic = roadmap.topicsById[topicId]
  if (!topic || !isStatus(status)) return state
  return updateRoadmap(state, roadmap.id, (rp) => {
    const topics = { ...rp.topics }
    const subtopics = { ...rp.subtopics }
    writeStatus(topics, topicId, status, now)
    if (status !== STATUS.IN_PROGRESS) {
      for (const s of topic.subtopics) writeStatus(subtopics, subtopicKey(topicId, s.id), status, now)
    }
    return { ...rp, topics, subtopics, lastStudied: { ...rp.lastStudied, [topicId]: now } }
  })
}

/**
 * Set a subtopic's status and keep the parent topic in step:
 * all subtopics completed → topic completed; any progress → topic at least in progress;
 * a completed topic with a subtopic reopened → topic back to in progress.
 */
export function setSubtopicStatus(state, roadmap, topicId, subtopicId, status, now = Date.now()) {
  const topic = roadmap.topicsById[topicId]
  if (!topic || !topic.subtopics.some((s) => s.id === subtopicId) || !isStatus(status)) return state
  return updateRoadmap(state, roadmap.id, (rp) => {
    const topics = { ...rp.topics }
    const subtopics = { ...rp.subtopics }
    writeStatus(subtopics, subtopicKey(topicId, subtopicId), status, now)

    const statuses = topic.subtopics.map((s) => subtopics[subtopicKey(topicId, s.id)]?.status ?? STATUS.NOT_STARTED)
    const current = topics[topicId]?.status ?? STATUS.NOT_STARTED
    let next = current
    if (statuses.every((s) => s === STATUS.COMPLETED)) next = STATUS.COMPLETED
    else if (current === STATUS.COMPLETED) next = STATUS.IN_PROGRESS
    else if (current === STATUS.NOT_STARTED && statuses.some((s) => s !== STATUS.NOT_STARTED)) {
      next = STATUS.IN_PROGRESS
    }
    if (next !== current) writeStatus(topics, topicId, next, now)

    return { ...rp, topics, subtopics, lastStudied: { ...rp.lastStudied, [topicId]: now } }
  })
}

export function markStudied(state, roadmapId, topicId, now = Date.now()) {
  return updateRoadmap(state, roadmapId, (rp) => ({
    ...rp,
    lastStudied: { ...rp.lastStudied, [topicId]: now },
  }))
}

export function setActiveRoadmap(state, roadmapId) {
  return state.activeRoadmapId === roadmapId ? state : { ...state, activeRoadmapId: roadmapId }
}

export function resetRoadmapProgress(state, roadmapId) {
  const roadmaps = { ...state.roadmaps }
  delete roadmaps[roadmapId]
  return { ...state, roadmaps }
}
