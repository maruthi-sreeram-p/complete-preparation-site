import { buildRoadmap } from '../roadmap/model.js'

/**
 * Content registry: the only place that knows where user data lives.
 *
 *   content/roadmaps/<roadmapId>/roadmap.json        roadmap structure
 *   content/roadmaps/<roadmapId>/topics/<id>.json    one learning page per topic
 *
 * Adding a roadmap or a topic is just adding files; no code changes are needed.
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

const roadmaps = Object.entries(roadmapFiles)
  .map(([path, raw]) => {
    const id = ROADMAP_PATH.exec(path)?.[1]
    if (!id) return null
    return buildRoadmap(raw, { id, contentIds: new Set(Object.keys(loadersByRoadmap[id] ?? {})) })
  })
  .filter(Boolean)
  .sort((a, b) => a.title.localeCompare(b.title))

export const listRoadmaps = () => roadmaps

export const getRoadmap = (id) => roadmaps.find((r) => r.id === id) ?? null

/** Resolves to the raw topic content JSON, or null when the topic has no content file yet. */
export async function loadTopicContent(roadmapId, contentId) {
  const loader = loadersByRoadmap[roadmapId]?.[contentId]
  return loader ? loader() : null
}
