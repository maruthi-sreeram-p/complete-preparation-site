import { buildRoadmap } from '../roadmap/model.js'

/**
 * Content registry: the only place that knows where user data lives.
 *
 *   content/roadmaps/<roadmapId>/roadmap.json        roadmap structure
 *   content/roadmaps/<roadmapId>/topics/<id>.json    one learning page per topic
 *
 * Adding a roadmap or a topic is just adding files; no code changes are needed.
 *
 * A topic normally shows its own file. Its `contentId` can instead be "<roadmapId>/<topicId>" to show a page of
 * another roadmap, so a subject taught in two trees is stored once (progress is still kept per roadmap).
 */
const roadmapFiles = import.meta.glob('/content/roadmaps/*/roadmap.json', { eager: true, import: 'default' })
const topicLoaders = import.meta.glob('/content/roadmaps/*/topics/*.json', { import: 'default' })

const ROADMAP_PATH = /^\/content\/roadmaps\/([^/]+)\/roadmap\.json$/
const TOPIC_PATH = /^\/content\/roadmaps\/([^/]+)\/topics\/([^/]+)\.json$/

const loadersByRoadmap = {}
for (const [path, loader] of Object.entries(topicLoaders)) {
  const match = TOPIC_PATH.exec(path)
  if (match) (loadersByRoadmap[match[1]] ??= {})[match[2]] = loader
}

/** [roadmapId, topicId] of the file behind a contentId, which may point into another roadmap. */
const locate = (roadmapId, contentId) => {
  const slash = contentId.indexOf('/')
  return slash === -1 ? [roadmapId, contentId] : [contentId.slice(0, slash), contentId.slice(slash + 1)]
}

const roadmaps = Object.entries(roadmapFiles)
  .map(([path, raw]) => {
    const id = ROADMAP_PATH.exec(path)?.[1]
    if (!id) return null
    const contentIds = new Set(Object.keys(loadersByRoadmap[id] ?? {}))
    for (const t of Array.isArray(raw.topics) ? raw.topics : []) {
      if (typeof t?.contentId === 'string' && t.contentId.includes('/')) {
        const [otherRoadmap, otherTopic] = locate(id, t.contentId)
        if (loadersByRoadmap[otherRoadmap]?.[otherTopic]) contentIds.add(t.contentId)
      }
    }
    const roadmap = buildRoadmap(raw, { id, contentIds })
    return { ...roadmap, order: raw.order ?? 99, shortTitle: raw.shortTitle ?? roadmap.title }
  })
  .filter(Boolean)
  .sort((a, b) => a.order - b.order || a.title.localeCompare(b.title))

export const listRoadmaps = () => roadmaps

export const getRoadmap = (id) => roadmaps.find((r) => r.id === id) ?? null

/** Resolves to the raw topic content JSON, or null when the topic has no content file yet. */
export async function loadTopicContent(roadmapId, contentId) {
  const [owner, topicId] = locate(roadmapId, contentId)
  const loader = loadersByRoadmap[owner]?.[topicId]
  return loader ? loader() : null
}
