/**
 * Tolerant normaliser for topic content JSON (see content/README.md).
 * Fills in missing ids/titles, accepts bare strings as markdown blocks,
 * and never throws, so a slightly wrong content file still renders.
 *
 * @returns {{ title?: string, source?: object, sections: Array<{id, type, title, subtopicId?, blocks: object[]}> }}
 */
export function normalizeTopicContent(raw) {
  const rawSections = Array.isArray(raw?.sections) ? raw.sections : []
  const usedIds = new Set()

  const sections = rawSections
    .filter((s) => s && typeof s === 'object')
    .map((s, index) => {
      let id = typeof s.id === 'string' && s.id ? s.id : `section-${index + 1}`
      while (usedIds.has(id)) id = `${id}-${index + 1}`
      usedIds.add(id)

      const blocks = (Array.isArray(s.blocks) ? s.blocks : [])
        .map((b) => (typeof b === 'string' ? { type: 'markdown', text: b } : b))
        .filter((b) => b && typeof b === 'object')

      return {
        id,
        type: typeof s.type === 'string' ? s.type : 'other',
        title: typeof s.title === 'string' ? s.title : '',
        subtopicId: typeof s.subtopicId === 'string' ? s.subtopicId : undefined,
        blocks,
      }
    })

  return {
    title: typeof raw?.title === 'string' ? raw.title : undefined,
    source: raw?.source && typeof raw.source === 'object' ? raw.source : undefined,
    sections,
  }
}

/** Parse a line spec like "3", "2-5" or "1,4-6" into a Set of 1-based line numbers. */
export function parseLineSpec(spec) {
  const lines = new Set()
  if (typeof spec === 'number') return lines.add(spec)
  if (Array.isArray(spec)) {
    spec.forEach((n) => Number.isFinite(n) && lines.add(n))
    return lines
  }
  if (typeof spec !== 'string') return lines
  for (const part of spec.split(',')) {
    const [a, b] = part.split('-').map((x) => parseInt(x.trim(), 10))
    if (!Number.isFinite(a)) continue
    const end = Number.isFinite(b) ? b : a
    for (let n = Math.min(a, end); n <= Math.max(a, end); n++) lines.add(n)
  }
  return lines
}
